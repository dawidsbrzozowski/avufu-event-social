#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publikator postow avufu na Instagram.
API: "Instagram API with Instagram Login" -> graph.instagram.com
(token uzytkownika IG, bez Facebook Page).

Jak dziala:
  - czyta pliki JSON z folderu queue/,
  - publikuje te, ktorych czas (publish_at) juz nadszedl,
  - udane przenosi do published/ (z linkiem do posta),
  - nieudane zostaja w queue/ ze statusem "error" i trescia bledu.

Zero zaleznosci - tylko biblioteka standardowa Pythona.
Uruchamiany przez .github/workflows/publish.yml (cron / recznie).

Sekrety (zmienne srodowiskowe), per profil (EVENT / TRAINING):
  <PROFIL>_IG_TOKEN    - dlugozyjacy token uzytkownika Instagram (60 dni)
  <PROFIL>_IG_USER_ID  - ID konta Instagram

Facebook (posty na strone FB) = osobne API, dorobimy pozniej. Na razie IG.
"""
import json, os, sys, time, glob, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone

GRAPH = "https://graph.instagram.com/" + os.environ.get("GRAPH_VERSION", "v23.0")
QUEUE_DIR, PUBLISHED_DIR, FAILED_DIR = "queue", "published", "failed"


def creds(profile):
    p = profile.upper()
    return os.environ.get(f"{p}_IG_TOKEN"), os.environ.get(f"{p}_IG_USER_ID")


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
        raise RuntimeError(f"Instagram API {e.code}: {e.read().decode()}")


def publish_instagram(token, ig_id, media, caption):
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
    mid = api(f"{ig_id}/media_publish", {"creation_id": cid, "access_token": token})["id"]
    try:
        return api(mid, {"fields": "permalink", "access_token": token}, "GET").get("permalink", mid)
    except Exception:
        return mid


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
        if post.get("status") not in (None, "pending"):
            continue
        if not is_due(post):
            print(f"Jeszcze nie czas: {os.path.basename(f)} ({post.get('publish_at')})")
            continue
        profile = post.get("profile", "event")
        token, ig = creds(profile)
        if not token:
            print(f"POMIJAM {os.path.basename(f)}: brak sekretow dla profilu '{profile}'")
            continue
        media, caption = post.get("media", []), post.get("caption", "")
        networks = post.get("networks", ["instagram"])
        try:
            results = {}
            if "instagram" in networks:
                results["instagram"] = publish_instagram(token, ig, media, caption)
            if "facebook" in networks:
                results["facebook"] = "POMINIETO (publikacja FB jeszcze nie skonfigurowana)"
            post.update(status="published",
                        published_at=datetime.now(timezone.utc).isoformat(),
                        results=results)
            with open(os.path.join(PUBLISHED_DIR, os.path.basename(f)), "w", encoding="utf-8") as fh:
                json.dump(post, fh, ensure_ascii=False, indent=2)
            os.remove(f)
            print(f"OPUBLIKOWANO {os.path.basename(f)} -> {results}")
            done += 1
        except Exception as e:
            post.update(status="error", error=str(e))
            with open(f, "w", encoding="utf-8") as fh:
                json.dump(post, fh, ensure_ascii=False, indent=2)
            print(f"BLAD {os.path.basename(f)}: {e}", file=sys.stderr)
    print(f"Gotowe. Opublikowano: {done}")


if __name__ == "__main__":
    main()
