#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publikator postow avufu na Instagram i Facebook.
API: Meta Graph API -> graph.facebook.com
IG: token (System User / uzytkownika) z instagram_content_publish, IG_USER_ID
    = Instagram Business Account id.
FB: token STRONY z pages_manage_posts, FB_PAGE_ID = id strony.

Jak dziala:
  - czyta pliki JSON z folderu queue/,
  - publikuje te, ktorych czas (publish_at) juz nadszedl,
  - udane przenosi do published/ (z linkiem do posta),
  - nieudane zostaja w queue/ ze statusem "error" i trescia bledu.

Zero zaleznosci - tylko biblioteka standardowa Pythona.
Uruchamiany przez .github/workflows/publish.yml (cron / recznie).

Sekrety (zmienne srodowiskowe), per profil (EVENT / TRAINING):
  <PROFIL>_IG_TOKEN        - token uzytkownika/System User z instagram_content_publish
  <PROFIL>_IG_USER_ID      - ID konta Instagram (Instagram Business Account)
  <PROFIL>_FB_PAGE_TOKEN   - token STRONY FB z pages_manage_posts (do publikacji na FB)
  <PROFIL>_FB_PAGE_ID      - ID strony FB

Rolka: jeden link .mp4/.mov w "media". IG publikuje ja jako Reels, a FB jako
wideo strony. Opcjonalne pole "cover" to link do okladki JPG.

Pole "networks" w poscie wybiera sieci: ["instagram"], ["facebook"] albo oba.
Post leci na dana siec tylko jesli sa jej sekrety; brak sekretow = post czeka
w kolejce (nie jest oznaczany jako opublikowany).
"""
import json, os, sys, time, glob, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone

GRAPH = "https://graph.facebook.com/" + os.environ.get("GRAPH_VERSION", "v23.0")
QUEUE_DIR, PUBLISHED_DIR, FAILED_DIR = "queue", "published", "failed"


def ig_creds(profile):
    p = profile.upper()
    return os.environ.get(f"{p}_IG_TOKEN"), os.environ.get(f"{p}_IG_USER_ID")


def fb_creds(profile):
    p = profile.upper()
    return os.environ.get(f"{p}_FB_PAGE_TOKEN"), os.environ.get(f"{p}_FB_PAGE_ID")


def published_ok(result):
    """Czy w tej sieci post juz realnie poszedl? (chroni przed dublem przy
    ponowieniu). Udana publikacja zapisuje link/id; blad leci wyjatkiem i nic
    nie zapisuje, wiec kazdy niepusty wynik = juz wyslane."""
    return bool(result)


def is_video(media):
    """Rolka = dokladnie jeden link do pliku .mp4 albo .mov."""
    if len(media) != 1:
        return False
    return urllib.parse.urlparse(media[0]).path.lower().endswith((".mp4", ".mov"))


def api(path, params, method="POST"):
    data = urllib.parse.urlencode(params).encode()
    if method == "POST":
        req = urllib.request.Request(f"{GRAPH}/{path}", data=data, method="POST")
    else:
        req = urllib.request.Request(f"{GRAPH}/{path}?" + data, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Graph API {e.code}: {e.read().decode()}")


def wait_for_video(token, cid, timeout=300):
    """IG przetwarza wideo dluzej niz grafike: czekamy na FINISHED."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = api(cid, {"fields": "status_code,status", "access_token": token}, "GET")
        code = r.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram odrzucil wideo: {r}")
        time.sleep(10)
    raise RuntimeError(f"Instagram nie przetworzyl wideo w {timeout} s")


def publish_instagram(token, ig_id, media, caption, cover=None):
    if not ig_id:
        raise RuntimeError("brak IG_USER_ID")
    if is_video(media):
        params = {"media_type": "REELS", "video_url": media[0], "caption": caption,
                  "share_to_feed": "true", "access_token": token}
        if cover:
            params["cover_url"] = cover
        cid = api(f"{ig_id}/media", params)["id"]
        wait_for_video(token, cid)
    elif len(media) == 1:
        cid = api(f"{ig_id}/media",
                  {"image_url": media[0], "caption": caption, "access_token": token})["id"]
    else:
        children = []
        for m in media:
            children.append(api(f"{ig_id}/media",
                                {"image_url": m, "is_carousel_item": "true",
                                 "access_token": token})["id"])
        cid = api(f"{ig_id}/media",
                  {"media_type": "CAROUSEL", "children": ",".join(children),
                   "caption": caption, "access_token": token})["id"]
    if not is_video(media):
        time.sleep(6)  # IG potrzebuje chwili na przetworzenie kontenera
    mid = api(f"{ig_id}/media_publish", {"creation_id": cid, "access_token": token})["id"]
    try:
        return api(mid, {"fields": "permalink", "access_token": token}, "GET").get("permalink", mid)
    except Exception:
        return mid


def publish_facebook(token, page_id, media, caption):
    """Publikuje na stronie FB. Zdjecie -> /photos, wiele zdjec -> /feed z
    attached_media, brak zdjec -> /feed (post tekstowy), plik .mp4/.mov ->
    /videos. Zwraca link lub id."""
    if not page_id:
        raise RuntimeError("brak FB_PAGE_ID")
    if not media:
        pid = api(f"{page_id}/feed", {"message": caption, "access_token": token})["id"]
        return f"https://www.facebook.com/{pid}"
    if is_video(media):
        vid = api(f"{page_id}/videos",
                  {"file_url": media[0], "description": caption, "access_token": token})["id"]
        return f"https://www.facebook.com/{page_id}/videos/{vid}"
    if len(media) == 1:
        r = api(f"{page_id}/photos",
                {"url": media[0], "caption": caption, "access_token": token})
        pid = r.get("post_id") or r.get("id")
        return f"https://www.facebook.com/{pid}"
    # wiele zdjec: wgraj kazde jako nieopublikowane, potem jeden post z galeria
    attached = {}
    for i, m in enumerate(media):
        fbid = api(f"{page_id}/photos",
                   {"url": m, "published": "false", "access_token": token})["id"]
        attached[f"attached_media[{i}]"] = json.dumps({"media_fbid": fbid})
    params = {"message": caption, "access_token": token}
    params.update(attached)
    pid = api(f"{page_id}/feed", params)["id"]
    return f"https://www.facebook.com/{pid}"


def is_due(post):
    t = post.get("publish_at")
    if not t:
        return True
    dt = datetime.fromisoformat(t)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt <= datetime.now(timezone.utc)


def main():
    for d in (PUBLISHED_DIR, FAILED_DIR):
        os.makedirs(d, exist_ok=True)
    files = sorted(glob.glob(os.path.join(QUEUE_DIR, "*.json")))
    if not files:
        print("Kolejka pusta."); return
    done = 0
    for f in files:
        with open(f, encoding="utf-8") as fh:
            post = json.load(fh)
        # publikowalne: brak statusu / pending / approved. Reszta (draft, hold,
        # error, published) jest pomijana - pozwala stageowac posta bez publikacji.
        if post.get("status") not in (None, "pending", "approved"):
            continue
        if not is_due(post):
            print(f"Jeszcze nie czas: {os.path.basename(f)} ({post.get('publish_at')})")
            continue
        profile = post.get("profile", "event")
        media, caption = post.get("media", []), post.get("caption", "")
        networks = post.get("networks", ["instagram", "facebook"])
        # brak sekretow dla ktorejs zadanej sieci -> zostaw post w kolejce
        missing = []
        if "instagram" in networks and not ig_creds(profile)[0]:
            missing.append("IG")
        if "facebook" in networks and not fb_creds(profile)[0]:
            missing.append("FB")
        if missing:
            print(f"POMIJAM {os.path.basename(f)}: brak sekretow {'+'.join(missing)} "
                  f"dla profilu '{profile}' (post czeka w kolejce)")
            continue
        results = dict(post.get("results") or {})  # zachowaj to, co juz poszlo
        try:
            if "instagram" in networks and not published_ok(results.get("instagram")):
                tok, ig = ig_creds(profile)
                results["instagram"] = publish_instagram(tok, ig, media, caption, post.get("cover"))
            if "facebook" in networks and not published_ok(results.get("facebook")):
                tok, page = fb_creds(profile)
                results["facebook"] = publish_facebook(tok, page, media, caption)
            post.update(status="published",
                        published_at=datetime.now(timezone.utc).isoformat(),
                        results=results)
            with open(os.path.join(PUBLISHED_DIR, os.path.basename(f)), "w", encoding="utf-8") as fh:
                json.dump(post, fh, ensure_ascii=False, indent=2)
            os.remove(f)
            print(f"OPUBLIKOWANO {os.path.basename(f)} -> {results}")
            done += 1
        except Exception as e:
            post.update(status="error", error=str(e), results=results)
            with open(f, "w", encoding="utf-8") as fh:
                json.dump(post, fh, ensure_ascii=False, indent=2)
            print(f"BLAD {os.path.basename(f)}: {e}", file=sys.stderr)
    print(f"Gotowe. Opublikowano: {done}")


if __name__ == "__main__":
    main()
