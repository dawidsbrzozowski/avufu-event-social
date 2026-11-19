# Kolejka postow (queue/)

Każdy post = jeden plik `.json` w tym folderze. Workflow `publish.yml` sprawdza
kolejkę, publikuje posty których czas (`publish_at`) już minął, a udane przenosi
do `published/`. Nieudane zostają tutaj ze statusem `error` i treścią błędu.

## Nazewnictwo pliku
`RRRR-MM-DD-GGMM-profil-NN.json`, np. `2026-11-03-0730-event-01.json`.
(Nazwa jest dowolna, ale taka ułatwia sortowanie i czytanie.)

## Pola

| Pole | Wymagane | Opis |
|---|---|---|
| `profile` | tak | `event`, `training` lub `heritage` — wybiera, których sekretów/kont użyć |
| `type` | nie | `feed` (domyślnie), `story` (Relacja 9:16, bez podpisu) albo `reel` (Rolka, wideo pionowe z podpisem) |
| `publish_at` | tak | Data i godzina z przesunięciem strefy, ISO 8601. Warszawa zimą = `+01:00`, latem = `+02:00`. Brak pola = publikuj od razu. |
| `networks` | nie | Lista: `["instagram","facebook"]` (domyślnie oba) |
| `media` | tak | Lista PUBLICZNYCH linków. Grafiki/wideo wrzucamy do folderu `social/` tego repo, link to `https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/....jpg`. **feed**: 1 link = post, wiele = karuzela. **story/reel**: 1 link (zdjęcie dla story, wideo `.mp4` dla reel / story-wideo). |
| `caption` | feed/reel | Treść posta (hashtagi w treści). Story podpis ignoruje. |
| `status` | — | Bramka publikacji. Publikowalne: brak pola / `"pending"` / `"approved"`. Pomijane (zostają w repo, nie publikują): `"draft"`, `"hold"`. Ustawia automat po próbie: `"published"` (sukces, plik → `published/`) albo `"error"` (błąd, zostaje tu z polem `error`). Dla postów z akceptacją Dawida użyj `"approved"`. |

## Przykład (pojedyncze zdjęcie)
```json
{
  "profile": "event",
  "publish_at": "2026-11-03T07:30:00+01:00",
  "networks": ["instagram", "facebook"],
  "media": ["https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/2026-w45/post1.jpg"],
  "caption": "Treść posta...\n\n#eventfirmowy #wroclaw #avufuEVENT",
  "status": "pending"
}
```

## Przykład (karuzela)
```json
{
  "profile": "training",
  "publish_at": "2026-11-04T10:00:00+01:00",
  "networks": ["instagram", "facebook"],
  "media": [
    "https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/training/2026-w45/slajd1.jpg",
    "https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/training/2026-w45/slajd2.jpg"
  ],
  "caption": "Treść...\n\n#szkolenia #HR #avufuTRAINING",
  "status": "pending"
}
```

## Przykład (Relacja / Story — 9:16, bez podpisu)
`type: story`, jeden link w `media` (zdjęcie `.png/.jpg` albo wideo `.mp4`). IG publikuje jako Relację, FB jako Relację strony. Podpis jest ignorowany.
```json
{
  "profile": "heritage",
  "type": "story",
  "publish_at": "2026-11-20T09:00:00+01:00",
  "networks": ["instagram", "facebook"],
  "media": ["https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/heritage/img-01.png"],
  "status": "approved"
}
```

## Przykład (Rolka / Reel — wideo pionowe z podpisem)
`type: reel`, jeden link `.mp4`/`.mov` w `media`. IG publikuje jako Reels, FB jako Reels strony. Pole `cover` (link do JPG) jest opcjonalne i dotyczy Instagrama.
```json
{
  "profile": "heritage",
  "type": "reel",
  "publish_at": "2026-11-20T18:00:00+01:00",
  "networks": ["instagram", "facebook"],
  "media": ["https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/heritage/vid-01.mp4"],
  "cover": "https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/heritage/okladka.jpg",
  "caption": "Treść rolki...\n\n#seekthecradle",
  "status": "approved"
}
```

## Ważne
- `media` muszą być PUBLICZNYMI linkami — Meta sama pobiera grafikę z URL-a.
  Grafiki wrzucamy do folderu `social/` tego repo i commitujemy. GitHub serwuje
  je od razu jako publiczne linki `https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/...`
  (repo jest publiczne, zero deployu na Hostinger, zero SSH). WAŻNE: najpierw
  zacommituj+zapushuj grafikę, DOPIERO potem post z linkiem do niej.
- Instagram: limit ~25 postów/dobę na konto. Grafiki JPG/PNG. **IG wymaga grafiki**
  (publiczny link) — posta bez `media` nie opublikuje.
- Facebook: publikuje zdjęcie, karuzelę albo **sam tekst** (gdy `media` puste).
- `networks` domyślnie = `["instagram","facebook"]`. Post leci na daną sieć tylko
  jeśli w GitHub są jej sekrety; brak sekretów = post czeka w kolejce.
- Stories z ankietami: tego API nie publikuje — zostają ręcznie z telefonu.
