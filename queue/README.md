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
| `profile` | tak | `event` lub `training` — wybiera, których sekretów/kont użyć |
| `publish_at` | tak | Data i godzina z przesunięciem strefy, ISO 8601. Warszawa zimą = `+01:00`, latem = `+02:00`. Brak pola = publikuj od razu. |
| `networks` | nie | Lista: `["instagram","facebook"]` (domyślnie oba) |
| `media` | tak | Lista PUBLICZNYCH linków do grafik. Grafiki wrzucamy do folderu `social/` tego repo, a link to `https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/....jpg`. 1 link = pojedynczy post, wiele = karuzela. |
| `caption` | tak | Treść posta (hashtagi w treści). |
| `status` | — | Ustawia automat: `pending` → `published` / `error`. Nowy post zostaw bez tego pola lub `"pending"`. |

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
