# Seek the Cradle — runbook kampanii grudniowej (26.11–31.12 2026)

Pełny zapis tego, co i jak zostało zrobione, żeby móc to odtworzyć, edytować i powtórzyć
dla kolejnych kampanii. Stan: 2026-11-25.

---

## 1. Co to jest

Kampania świąteczna marki **Seek the Cradle** (przewodniki PDF o polskich korzeniach,
sprzedaż na Etsy/Whop). **36 postów** na Instagram + Facebook, po jednym dziennie
26.11–31.12, przypiętych do okazji (Thanksgiving, Black Friday, Mikołajki, Wigilia, Sylwester).

Konta:
- IG `@seekthecradle` → `HERITAGE_IG_USER_ID = 17841480852486666`
- FB strona Seek the Cradle → **Graph page id `1508324085691105`** (NIE `61596935420553` z URL-a)
- Oba przypięte do bota `avufu-publisher-bot`; FB token wyznaczany w locie z SUAT w workflow.

---

## 2. Gdzie co leży

| Element | Ścieżka |
|---|---|
| Plan postów (źródło prawdy) | `C:\Users\dbgro\Downloads\Seek the Cradle – plan postów FB IG 26.11–31.12 - Plan postów.csv` |
| Grafiki pogrupowane per post (robocze) | `C:\Users\dbgro\Desktop\MYHeritageExpirience\kampania-26-11-grafiki\` |
| Grafiki w repo (hostowane) | `social/heritage/kampania/P01..P36(.png/.jpg)` |
| Posty (kolejka) | `queue/{data}-0700et-heritage-pNN.json` |
| Generator | `tools/gen_kampania.py` |
| Publikator | `scripts/publish.py` |
| Workflow (cron co 15 min) | `.github/workflows/publish.yml` |
| Oryginalne źródła grafik | `Desktop\MYHeritageExpirience\{SoMe, grafiki/etsy, grafiki/okladki, Multimedia}` |

---

## 3. Architektura publikacji (przypomnienie)

GitHub Actions (cron `*/15`) → `scripts/publish.py` → Meta Graph API. Posty = pliki JSON
w `queue/`. Grafiki pobierane przez Meta wprost z `raw.githubusercontent.com` (repo publiczne,
zero własnego serwera). Udany post: `queue/` → `published/` (commit bota). Błąd: zostaje
w `queue/` ze `status: error`. Szczegóły: `PUBLIKACJA-SETUP-META.md`.

Pola postu: `profile` (`heritage`), `type` (`feed` = zdjęcie lub karuzela), `publish_at`
(ISO z offsetem), `networks`, `media` (lista URL), `status` (`approved`/`pending`/null = idzie),
oraz podpisy (patrz niżej).

---

## 4. Co konkretnie zrobiono (kolejność kroków)

1. **Znaleziono plan** — był w `Downloads`, nie na Desktopie. 14 kolumn, wiersze P01–P36,
   każdy z datą, grafiką, typem (pojedyncza/karuzela), opisem FB, hashtagami IG i FB.
2. **Zebrano grafiki w jeden folder** `kampania-26-11-grafiki\`, nazwane numerem posta:
   pojedyncze `P03.png`, karuzele `P02-1..4`, `P05/06/12/14/17-1..3`, `P24-1..2`.
   50 plików, oryginały nietknięte (kopie). Mapowanie 1:1 z kolumną „Nr" planu.
   Uwaga: NIE spłaszczać po nazwie bazowej — pliki etsy to `01.jpg` w 4 różnych podfolderach,
   kolidują; dlatego przemianowane na `Pnn`.
3. **Sync repo** — lokalny klon był 12 commitów za origin i mylił („zaległe posty" to był
   artefakt starego klonu). Po `merge --ff-only origin/main`: kolejka pusta, a wszystkie
   posty z 19–23.11 (w tym reele/wideo) były już w `published/`. Pipeline działa też dla wideo.
4. **Grafiki do repo** — skopiowane do `social/heritage/kampania/`.
5. **Rozszerzono `publish.py`** o osobne podpisy per sieć: pola `caption_ig` / `caption_fb`
   (brak → fallback do wspólnego `caption`). Zmiana wstecznie kompatybilna, nie rusza
   Event/Training. W `main()`: `cap_ig = post.get("caption_ig") or caption` (analogicznie fb),
   przekazywane do `do_instagram` / `do_facebook`.
6. **Generator `tools/gen_kampania.py`** — czyta CSV i tworzy 36 JSONów:
   - `media` = pliki `Pnn.*` / `Pnn-*` z `social/heritage/kampania/`, jako URL raw.
   - `caption_fb` = opis + hashtagi FB (z klikalnym linkiem).
   - `caption_ig` = opis z URL-ami zamienionymi na „Link in bio" (regex `https?://\S+`) + hashtagi IG.
7. **Harmonogram** — ostatecznie **7:00 ET (EST, `-05:00`)** na każdy dzień (poranek Polonii
   w USA), pierwotnie było 20:00 PL. `publish_at = {data}T07:00:00-05:00`.
8. **Walidacja** — sprawdzono, że żaden URL nie wyciekł na IG; grafiki zwracają `200 image/*`
   z raw. Commit + push na `main`.

---

## 5. Jak edytować / odtworzyć

**Zmiana treści lub godziny wszystkich postów:**
1. Edytuj plan CSV (treść) albo `tools/gen_kampania.py` (godzina = linia `publish_at`,
   nazwa pliku = linia `fname`).
2. Usuń stare: `git rm queue/*-heritage-p*.json`
3. Regeneruj: `python tools/gen_kampania.py`
4. `git add queue tools/gen_kampania.py && git commit && git push`

**Pojedynczy post** — edytuj bezpośrednio `queue/{...}-heritage-pNN.json` i push.

**Test na żywo bez czekania** — w jednym poście ustaw `publish_at` na teraz (lub przeszłość),
push; albo GitHub → Actions → „Publikuj posty (IG + FB)" → Run workflow. Cron i tak sprawdza
co 15 min. Post wychodzi tylko gdy `publish_at ≤ teraz` — **nigdy wcześniej**, co najwyżej
później (cron GitHuba potrafi się spóźnić o kilka–kilkadziesiąt minut).

**Wstrzymać post** — zmień `status` na `hold` (albo cokolwiek poza approved/pending/null).

---

## 6. Pula NIEUŻYTYCH materiałów (na dodatkowe posty + reklamy)

Baza: `C:\Users\dbgro\Desktop\MYHeritageExpirience\`
- `grafiki/etsy/` nieużyte: beginning 02,07,08,09 · gift-edition 08 · going-back 07,09.
- `SoMe/pomelli_creative_image_9_16_1119 (4)(6)(9)(11).png` — 4 grafiki 9:16.
- `SoMe/pomelli_creative_video_9_16_1119*.mp4` — **5 wideo 9:16** (kampania nie miała reeli).
- `grafiki/okladki/workbook.png` + wersje print `*-2550x3300.png` + `grafiki/etsy/_covers/`.
- **`Multimedia/`** (NOWE, 25.11): obrazy `beginning 1`, `going back 1`, `workbook 1–6`,
  `Adwentowa świeca i opłatek`, `Mglista droga…`, `Nostalgiczne listy…`,
  `Rustykalna martwa natura…`, `Rustykalne pakowanie…`, `jakaś reklama 1`; **wideo**
  `1.mp4` + 6× `hf_2026*.mp4`; brief `prompt-cc-grafiki-poprawki.md`.
  Na Pulpicie: `prompt-cc-kampania-26-11-9-12.md`.

Pomysł na dalej: reele z wideo (pomelli/hf), karuzele z nieużytych etsy, kreacje pod
Whop/Meta Ads.

---

## 7. Pułapki / lekcje

- **Zawsze `git fetch` + sprawdź origin/main przed pracą** — lokalny klon bywa daleko w tyle,
  bo bot commituje publikacje prosto na GitHub.
- FB page id to `1508324085691105`, nie liczba z URL `profile.php`.
- Grafiki etsy mają kolidujące nazwy bazowe (`01.jpg` × 4) — nie spłaszczać bez prefiksu.
- Wideo z raw bywa serwowane jako `application/octet-stream`, ale Meta i tak przyjęła reele
  (zweryfikowane 19–22.11). Gdyby kiedyś odrzuciła — fallback: inny host mp4.
- Konsola Windows (cp1250) wywala się na emoji przy `print` — to błąd wyświetlania, nie danych.
