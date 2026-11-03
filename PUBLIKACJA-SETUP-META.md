# Setup publikacji IG + FB (darmowo, przez Graph API) — dla Dawida

Cel: agenci (Scena/Treni) wrzucają posty do `queue/`, a GitHub Actions publikuje
je o czasie na Instagram i Facebook — **za darmo, bez App Review** (bo publikujemy
na WŁASNE konta: wystarczy tryb deweloperski aplikacji Meta + rola „Tester").

Robisz to **raz na profil**. Ja prowadzę krok po kroku — jak coś nie zagra,
wklej mi komunikat błędu.

---

## Wymagania wstępne (per profil: EVENT i TRAINING)
- Konto **Instagram** musi być **Business** lub **Creator** (nie prywatne).
- Konto IG **spięte ze stroną Facebook** (Ustawienia IG → Udostępnianie w innych aplikacjach / Linked accounts).
- Masz dostęp admina do tej strony FB.

---

## KROK 1 — Aplikacja Meta (jedna, obsłuży wszystkie profile)
1. Wejdź na https://developers.facebook.com/apps → **Create App**.
2. Typ: **Business**. Nazwa np. „avufu-publisher". Zostaw w trybie **Development**.
3. W aplikacji dodaj produkt **Instagram** (Graph API) oraz **Facebook Login for Business**.

## KROK 2 — Dodaj swoje konta IG jako „Instagram Tester"
1. W panelu aplikacji: **App roles → Roles** (albo Instagram → API setup).
2. Dodaj konto IG (`event.avufu`, potem training) jako **Instagram Tester**.
3. Zaakceptuj zaproszenie **w aplikacji Instagram**: Ustawienia → Dla profesjonalistów /
   Aplikacje i witryny → Zaproszenia testera → Akceptuj.
   > To jest ten magiczny krok, dzięki któremu NIE potrzeba App Review.

## KROK 3 — Wygeneruj token i pobierz ID (per profil)
Najprościej w **Graph API Explorer** (https://developers.facebook.com/tools/explorer):
1. Wybierz swoją aplikację (prawy górny róg).
2. „Generate Access Token" i zaznacz uprawnienia (scopes):
   `instagram_basic`, `instagram_content_publish`, `pages_show_list`,
   `pages_read_engagement`, `pages_manage_posts`, `business_management`.
3. Zatwierdź okno logowania/uprawnień.
4. **ID strony FB:** zapytanie `GET me/accounts` → znajdź stronę → pole `id` = `PAGE_ID`.
5. **ID konta IG:** zapytanie `GET {PAGE_ID}?fields=instagram_business_account`
   → `instagram_business_account.id` = `IG_USER_ID`.
6. **Token długożyjący:** krótki token z Explorera zamień na 60-dniowy, a z niego
   weź token STRONY (ten dla stron jest trwały). Ten moment zrobimy razem —
   wklej mi krótki token *prywatnie* albo przeprowadzę Cię przez 2 zapytania
   (`oauth/access_token` + `me/accounts`), żeby wyjąć token strony.
   > Tokenów NIE wklejaj do kodu ani do repo — tylko do GitHub Secrets (krok 4).

## KROK 4 — Wpisz sekrety w GitHub
Repo `avufu-event-social` → **Settings → Secrets and variables → Actions → New repository secret**.
Dodaj (dla każdego profilu osobno):

**WAŻNE — nazwy muszą być DOKŁADNIE takie (tak czyta je `scripts/publish.py` i `publish.yml`).**
Metoda, która zadziałała, to **System User token** (SUAT, nie wygasa), nie „Instagram
Tester" z KROKU 2 — KROK 1–3 powyżej są historyczne. Realne 4 sekrety na profil:

| Sekret | Wartość |
|---|---|
| `EVENT_IG_TOKEN` | token System Usera (`instagram_content_publish`) dla `event.avufu` |
| `EVENT_IG_USER_ID` | IG Business Account id konta `event.avufu` |
| `EVENT_FB_PAGE_TOKEN` | token STRONY FB „Avufu EVENT" (`pages_manage_posts`) |
| `EVENT_FB_PAGE_ID` | id strony FB „Avufu EVENT" (`1298920449981786`) |
| `TRAINING_IG_TOKEN` | token System Usera (`instagram_content_publish`) dla `training.avufu` |
| `TRAINING_IG_USER_ID` | IG Business Account id `training.avufu` (`17841451374149506`) |
| `TRAINING_FB_PAGE_TOKEN` | token STRONY FB „Training.avufu" (`pages_manage_posts`) |
| `TRAINING_FB_PAGE_ID` | id strony FB „Training.avufu" (`1453902861133145`) |

(Sekrety SFTP_* są już NIEużywane — grafiki hostujemy przez `raw.githubusercontent.com`,
deploy na Hostinger usunięty. Można je skasować.)

## KROK 5 — Test ręczny
1. Agent (lub Ty) wrzuca jeden testowy plik do `queue/` z `publish_at` w przeszłości
   i prawdziwym linkiem do grafiki w `media`.
2. GitHub → zakładka **Actions** → „Publikuj posty (IG + FB)" → **Run workflow**.
3. Jak wyjdzie zielone i post pojawi się na profilu — działa.
4. Wtedy **odkomentuj `schedule`** w `.github/workflows/publish.yml` → publikacja chodzi sama.

---

## Odświeżanie tokenów
Token strony wyciągnięty z tokenu długożyjącego jest zwykle trwały, ale jak
publikacja kiedyś zacznie zwracać błąd „token expired" — generujemy nowy
(powtórka kroku 3) i podmieniamy sekret. Przypomnę o tym, jeśli zobaczę błąd.

## Limity i uwagi
- Instagram: ~25 postów/dobę na konto; grafiki JPG/PNG; wideo/reels to osobny tor.
- Cron GitHub Actions bywa opóźniony o kilka minut — bez znaczenia dla postów.
- Workflow usypia po 60 dniach bezczynności repo (łatwo wznowić jednym „Run workflow").
