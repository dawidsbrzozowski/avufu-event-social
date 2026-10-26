# Setup repo „avufu-event-social" (dla Dawida)

Cel: Scena (agentka w chmurze) wrzuca grafiki do repo GitHub → GitHub Actions
automatycznie wgrywa je na Hostinger do `event.avufu.com/social/` → Metricool
pobiera je jako publiczne linki.

## Co musi zrobić Dawid (jednorazowo)

1. **Utwórz repo na GitHub** (może być prywatne), np. `avufu-event-social`.
   Wrzuć do niego zawartość tego folderu (`.github/`, `social/`).

2. **Klucz SSH w formacie OpenSSH** (GitHub Actions nie przyjmuje `.ppk` z PuTTY):
   - Opcja A (zalecana): wygeneruj nową parę kluczy OpenSSH:
     `ssh-keygen -t ed25519 -f avufu_gh_deploy -C "github-actions-social"`
     - klucz **publiczny** (`avufu_gh_deploy.pub`) → wklej w hPanel Hostinger → SSH → „Zarządzaj kluczami SSH".
     - klucz **prywatny** (`avufu_gh_deploy`, cała zawartość) → do sekretu GitHub (pkt 3).
   - Opcja B: skonwertuj istniejący `avufu_sftp.ppk` w PuTTYgen → Export OpenSSH key.

3. **Dodaj sekrety w repo** (GitHub → Settings → Secrets and variables → Actions → New repository secret):
   - `SFTP_HOST` = `141.136.45.137`
   - `SFTP_PORT` = `65002`
   - `SFTP_USER` = `u112202089`
   - `SFTP_KEY`  = cała zawartość prywatnego klucza OpenSSH (z pkt 2)
   > Klucza NIE wklejaj nigdzie w czacie ani w kodzie — tylko jako sekret.

4. **Daj Scenie dostęp do repo** (Collaborator) albo token, żeby mogła pushować do `main`.

## Jak to działa potem
- Scena robi `git push` plików do `social/...` na gałąź `main`.
- Workflow `.github/workflows/deploy-social.yml` odpala się (tylko dla zmian w `social/**`)
  i wgrywa pliki przez SCP do `/home/u112202089/domains/event.avufu.com/public_html/social`.
- Plik `social/2026-w44/post1.jpg` → `https://event.avufu.com/social/2026-w44/post1.jpg`.

## Bezpieczeństwo / izolacja
- Workflow pisze wyłącznie do podkatalogu `social/` (źródło `source: social/**`).
- Reszta strony event.avufu.com NIE jest dotykana.
- Katalog `/social/` ma wyłączony listing (LiteSpeed zwraca 403 na `/social/`), więc nikt nie przegląda listy plików — działają tylko bezpośrednie linki do konkretnych grafik.

## Alternatywa (bez klucza SSH w GitHub): wbudowany Git Hostingera
hPanel → Zaawansowane → **GIT**: repozytorium = URL repo, gałąź = `main`,
katalog instalacji = `social`. Hostinger pobiera repo do `public_html/social`.
Auto-deploy: skopiuj z hPanel „webhook URL" i dodaj go w GitHub (repo → Settings → Webhooks),
żeby push wyzwalał wdrożenie. Minus: wdraża CAŁE repo do `/social` (więc repo powinno
zawierać tylko grafiki). Dlatego czystsze jest rozwiązanie z GitHub Actions powyżej.
