# Narzędzia Sceny (Avufu Event)
- `generator.py` – generuje grafiki IG/FB w identyfikacji Avufu Event z pliku JSON (opis pól w nagłówku pliku).
- `setup-fonts.sh` – jednorazowo pobiera czcionki (Manrope, Playfair Display).
- `specs/` – treści opublikowanych postów (JSON), jeden plik na dzień.

Użycie: `./setup-fonts.sh && python3 generator.py specs/2026-10-27.json ../social/2026-w44/p27`
Grafiki trafiają do `social/RRRR-wTT/…` i są dostępne publicznie pod
`https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/…`
