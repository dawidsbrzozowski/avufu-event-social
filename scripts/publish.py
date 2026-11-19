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

Typy postow (pole "type"):
  - "feed"  (domyslnie) - zdjecie / karuzela (IG wymaga <=4:5) / FB sam tekst,
  - "story" - Relacja (IG Stories / FB photo_stories|video_stories), 9:16, bez podpisu,
  - "reel"  - Rolka (IG Reels / FB video_reels), wideo pionowe 9:16, z podpisem.
Zdjecie vs wideo rozpoznawane po rozszerzeniu media (.mp4/.mov = wideo).
Dla reel opcjonalne pole "cover" (link do okladki JPG) dotyczy Instagrama.

Zero zaleznosci - tylko biblioteka standardowa Pythona.
Uruchamiany przez .github/workflows/publish.yml (cron / recznie) albo lokalnie.

Sekrety (zmienne srodowiskowe), per profil (EVENT / TRAINING / HERITAGE):
  <PROFIL>_IG_TOKEN        - token uzytkownika/System User z instagram_content_publish
  <PROFIL>_IG_USER_ID      - ID konta Instagram (Instagram Business Account)
  <PROFIL>_FB_PAGE_TOKEN   - token STRONY FB z pages_manage_posts (do publikacji na FB)
  <PROFIL>_FB_PAGE_ID      - ID strony FB

Pole "networks" w poscie wybiera sieci: ["instagram"], ["facebook"] albo oba.
Post leci na dana siec tylko jesli sa jej sekrety; brak sekretow = post czeka
w kolejce (nie jest oznaczany jako opublikowany).
"""
import json, os, sys, time, glob, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone

GRAPH = "https://graph.facebook.com/" + os.environ.get("GRAPH_VERSION", "v23.0")
QUEUE_DIR, PUBLISHED_DIR, FAILED_DIR = "queue", "published", "failed"
VIDEO_EXT = (".mp4", ".mov", ".m4v")


def is_video(url):
    return url.lower().split("?")[0].endswith(VIDEO_EXT)


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


def api(path, params, method="POST"):
    data = urllib.parse.urlencode(params).encode()
    if method == "POST":
        req = urllib.request.Request(f"{GRAPH}/{path}", data=data, method="POST")
    else:
        req = urllib.request.Request(f"{GRAPH}/{path}?" + data.decode(), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Graph API {e.code}: {e.read().decode()}")


def rupload(upload_url, token, file_url):
    """Faza upload dla FB Reels/Stories wideo: Meta sama pobiera plik z file_url
    (hosted upload), bez wysylania bajtow z naszej strony."""
    req = urllib.request.Request(upload_url, data=b"", method="POST")
    req.add_header("Authorization", f"OAuth {token}")
    req.add_header("file_url", file_url)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"rupload {e.code}: {e.read().decode()}")


# ---------- Instagram ----------

def ig_wait_container(token, cid, tries=30, delay=10):
    """Wideo (Reels/Stories video) wymaga przetworzenia kontenera przed publikacja."""
    for _ in range(tries):
        st = api(cid, {"fields": "status_code", "access_token": token}, "GET").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"IG kontener {st} ({cid})")
        time.sleep(delay)
    raise RuntimeError(f"IG kontener nie gotowy w czasie ({cid})")


def ig_publish_container(token, ig_id, cid):
    mid = api(f"{ig_id}/media_publish", {"creation_id": cid, "access_token": token})["id"]
    try:
        return api(mid, {"fields": "permalink", "access_token": token}, "GET").get("permalink", mid)
    except Exception:
        return mid


def publish_instagram(token, ig_id, media, caption):
    """Feed: pojedyncze zdjecie lub karuzela."""
    if not ig_id:
        raise RuntimeError("brak IG_USER_ID")
    if len(media) == 1:
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
    time.sleep(6)  # IG potrzebuje chwili na przetworzenie kontenera
    return ig_publish_container(token, ig_id, cid)


def publish_instagram_story(token, ig_id, url):
    """Relacja IG (9:16). Zdjecie albo wideo. Bez podpisu."""
    if not ig_id:
        raise RuntimeError("brak IG_USER_ID")
    key = "video_url" if is_video(url) else "image_url"
    cid = api(f"{ig_id}/media",
              {"media_type": "STORIES", key: url, "access_token": token})["id"]
    if is_video(url):
        ig_wait_container(token, cid)
    else:
        time.sleep(6)
    return ig_publish_container(token, ig_id, cid)


def publish_instagram_reel(token, ig_id, url, caption, cover=None, share_to_feed=True):
    """Rolka IG. Wideo pionowe 9:16, z podpisem. Opcjonalna okladka (cover)."""
    if not ig_id:
        raise RuntimeError("brak IG_USER_ID")
    params = {"media_type": "REELS", "video_url": url, "caption": caption,
              "share_to_feed": "true" if share_to_feed else "false",
              "access_token": token}
    if cover:
        params["cover_url"] = cover
    cid = api(f"{ig_id}/media", params)["id"]
    ig_wait_container(token, cid)
    return ig_publish_container(token, ig_id, cid)


# ---------- Facebook ----------

def fb_wait_video(token, vid, tries=36, delay=5):
    """Czeka az FB przetworzy wgrane wideo (Reels/Stories)."""
    for _ in range(tries):
        try:
            st = api(vid, {"fields": "status", "access_token": token}, "GET").get("status", {})
        except RuntimeError:
            time.sleep(delay); continue
        phase = (st.get("processing_phase") or {}).get("status") or st.get("video_status")
        if phase in ("complete", "ready", "published"):
            return
        if phase == "error":
            raise RuntimeError(f"FB wideo ERROR ({vid}): {st}")
        time.sleep(delay)
    # nie podnosimy wyjatku - finish z video_state=PUBLISHED opublikuje po przetworzeniu


def publish_facebook(token, page_id, media, caption):
    """Feed: zdjecie -> /photos, wiele zdjec -> /feed z attached_media,
    brak zdjec -> /feed (post tekstowy). Zwraca link lub id."""
    if not page_id:
        raise RuntimeError("brak FB_PAGE_ID")
    if not media:
        pid = api(f"{page_id}/feed", {"message": caption, "access_token": token})["id"]
        return f"https://www.facebook.com/{pid}"
    if len(media) == 1:
        r = api(f"{page_id}/photos",
                {"url": media[0], "caption": caption, "access_token": token})
        pid = r.get("post_id") or r.get("id")
        return f"https://www.facebook.com/{pid}"
    attached = {}
    for i, m in enumerate(media):
        fbid = api(f"{page_id}/photos",
                   {"url": m, "published": "false", "access_token": token})["id"]
        attached[f"attached_media[{i}]"] = json.dumps({"media_fbid": fbid})
    params = {"message": caption, "access_token": token}
    params.update(attached)
    pid = api(f"{page_id}/feed", params)["id"]
    return f"https://www.facebook.com/{pid}"


def publish_facebook_story(token, page_id, url):
    """Relacja FB. Zdjecie (photo_stories) albo wideo (video_stories)."""
    if not page_id:
        raise RuntimeError("brak FB_PAGE_ID")
    if is_video(url):
        start = api(f"{page_id}/video_stories", {"upload_phase": "start", "access_token": token})
        vid, up = start["video_id"], start["upload_url"]
        rupload(up, token, url)
        fb_wait_video(token, vid)
        api(f"{page_id}/video_stories",
            {"upload_phase": "finish", "video_id": vid, "access_token": token})
        return f"story-video:{vid}"
    photo_id = api(f"{page_id}/photos",
                   {"url": url, "published": "false", "access_token": token})["id"]
    r = api(f"{page_id}/photo_stories", {"photo_id": photo_id, "access_token": token})
    return r.get("post_id") or f"story-photo:{photo_id}"


def publish_facebook_reel(token, page_id, url, caption):
    """Rolka FB. Wideo pionowe 9:16, z opisem."""
    if not page_id:
        raise RuntimeError("brak FB_PAGE_ID")
    start = api(f"{page_id}/video_reels", {"upload_phase": "start", "access_token": token})
    vid, up = start["video_id"], start["upload_url"]
    rupload(up, token, url)
    fb_wait_video(token, vid)
    api(f"{page_id}/video_reels",
        {"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
         "description": caption, "access_token": token})
    return f"https://www.facebook.com/reel/{vid}"


# ---------- rozdzielacz typow ----------

def do_instagram(ptype, token, ig_id, media, caption, cover=None):
    if ptype == "story":
        return publish_instagram_story(token, ig_id, media[0])
    if ptype == "reel":
        return publish_instagram_reel(token, ig_id, media[0], caption, cover)
    return publish_instagram(token, ig_id, media, caption)


def do_facebook(ptype, token, page_id, media, caption):
    if ptype == "story":
        return publish_facebook_story(token, page_id, media[0])
    if ptype == "reel":
        return publish_facebook_reel(token, page_id, media[0], caption)
    return publish_facebook(token, page_id, media, caption)


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
        ptype = post.get("type", "feed")
        media, caption = post.get("media", []), post.get("caption", "")
        cover = post.get("cover")
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
                results["instagram"] = do_instagram(ptype, tok, ig, media, caption, cover)
            if "facebook" in networks and not published_ok(results.get("facebook")):
                tok, page = fb_creds(profile)
                results["facebook"] = do_facebook(ptype, tok, page, media, caption)
            post.update(status="published",
                        published_at=datetime.now(timezone.utc).isoformat(),
                        results=results)
            with open(os.path.join(PUBLISHED_DIR, os.path.basename(f)), "w", encoding="utf-8") as fh:
                json.dump(post, fh, ensure_ascii=False, indent=2)
            os.remove(f)
            print(f"OPUBLIKOWANO {os.path.basename(f)} ({ptype}) -> {results}")
            done += 1
        except Exception as e:
            post.update(status="error", error=str(e), results=results)
            with open(f, "w", encoding="utf-8") as fh:
                json.dump(post, fh, ensure_ascii=False, indent=2)
            print(f"BLAD {os.path.basename(f)}: {e}", file=sys.stderr)
    print(f"Gotowe. Opublikowano: {done}")


if __name__ == "__main__":
    main()
