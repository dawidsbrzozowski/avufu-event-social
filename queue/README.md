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
| `media` | tak | Lista PUBLICZNYCH linków do grafik (np. `https://event.avufu.com/social/...jpg`). 1 link = pojedynczy post, wiele = karuzela. |
| `caption` | tak | Treść posta (hashtagi w treści). |
| `status` | — | Ustawia automat: `pending` → `published` / `error`. Nowy post zostaw bez tego pola lub `"pending"`. |

## Przykład (pojedyncze zdjęcie)
```json
{
  "profile": "event",
  "publish_at": "2026-11-03T07:30:00+01:00",
  "networks": ["instagram", "facebook"],
  "media": ["https://event.avufu.com/social/2026-w45/post1.jpg"],
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
    "https://event.avufu.com/social/training/2026-w45/slajd1.jpg",
    "https://event.avufu.com/social/training/2026-w45/slajd2.jpg"
  ],
  "caption": "Treść...\n\n#szkolenia #HR #avufuTRAINING",
  "status": "pending"
}
```

## Ważne
- `media` muszą być PUBLICZNYMI linkami — Meta sama pobiera grafikę z URL-a.
  Grafiki wrzucamy jak dotąd do `social/...`, a deploy stawia je pod
  `event.avufu.com/social/...` (ten sam mechanizm, którego już używasz).
- Instagram: limit ~25 postów/dobę na konto. Grafiki JPG/PNG.
- Stories z ankietami: tego API nie publikuje — zostają ręcznie z telefonu.
