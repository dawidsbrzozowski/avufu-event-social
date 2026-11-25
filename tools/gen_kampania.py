#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generuje 36 postow kampanii Seek the Cradle (26.11-31.12) do queue/ z CSV planu.
Zrodlo grafik: social/heritage/kampania/P01.. (nazwane numerem posta).
IG dostaje "Link in bio" zamiast URL + dluzsze hashtagi IG; FB dostaje klikalny link."""
import csv, json, re, glob, os

CSV = r"C:/Users/dbgro/Downloads/Seek the Cradle – plan postów FB IG 26.11–31.12 - Plan postów.csv"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAMP_DIR = os.path.join(REPO, "social", "heritage", "kampania")
QUEUE = os.path.join(REPO, "queue")
BASE = "https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/heritage/kampania/"

URL_RE = re.compile(r"https?://\S+")


def ig_body(fb_body):
    # na IG linki nie sa klikalne -> zamien URL na "Link in bio"
    return URL_RE.sub("Link in bio", fb_body).rstrip()


def media_for(nr):
    # nr = "P01"; dopasuj P01.ext oraz P01-1.ext.. (karuzela), posortowane
    files = sorted(
        glob.glob(os.path.join(KAMP_DIR, nr + ".*"))
        + glob.glob(os.path.join(KAMP_DIR, nr + "-*"))
    )
    return [BASE + os.path.basename(f) for f in files]


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
    made = 0
    for r in rows:
        nr = (r["Nr"] or "").strip()           # P01..P36
        date = (r["Data"] or "").strip()        # 2026-11-26
        if not nr or not date:
            continue
        body = (r['Opis posta (FB; na IG link → "Link in bio")'] or "").strip()
        ig_tags = (r["Hashtagi IG"] or "").strip()
        fb_tags = (r["Hashtagi FB"] or "").strip()
        media = media_for(nr)
        if not media:
            print("BRAK GRAFIKI dla", nr); continue
        cap_fb = body + ("\n\n" + fb_tags if fb_tags else "")
        cap_ig = ig_body(body) + ("\n\n" + ig_tags if ig_tags else "")
        post = {
            "profile": "heritage",
            "type": "feed",
            "publish_at": f"{date}T07:00:00-05:00",  # 7:00 ET (EST, zima) = 12:00 UTC = 13:00 PL
            "networks": ["instagram", "facebook"],
            "media": media,
            "caption_fb": cap_fb,
            "caption_ig": cap_ig,
            "status": "approved",
        }
        fname = f"{date}-0700et-heritage-{nr.lower()}.json"
        with open(os.path.join(QUEUE, fname), "w", encoding="utf-8") as fh:
            json.dump(post, fh, ensure_ascii=False, indent=2)
        made += 1
        print(f"OK {fname}  media={len(media)}")
    print(f"\nWygenerowano: {made} postow")


if __name__ == "__main__":
    main()
