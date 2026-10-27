"""Buduje szablony maili HTML Avufu Event (tabele + style inline, szer. 600 px)."""
import pathlib
IMG = 'https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/email/'
URL = 'https://event.avufu.com/firmowa-wigilia.html'
F = "font-family:Manrope,'Segoe UI',Arial,Helvetica,sans-serif;"
SER = "font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-style:italic;"

def p(t, size=16, color='#d9d3e6', mb=16):
    return f'<p style="{F}font-size:{size}px;line-height:1.6;color:{color};margin:0 0 {mb}px 0;">{t}</p>'

def bullets(items):
    rows = ''.join(f'<tr><td valign="top" style="{SER}font-size:18px;color:#c6a8f7;padding:0 12px 12px 0;line-height:1.5;">–</td>'
                   f'<td style="{F}font-size:16px;line-height:1.55;color:#d9d3e6;padding:0 0 12px 0;"><strong style="color:#ffffff;">{a}</strong> – {b}</td></tr>'
                   for a, b in items)
    return f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 8px 0;">{rows}</table>'

def button(label):
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:8px 0 24px 0;"><tr>'
            f'<td bgcolor="#a855f7" style="border-radius:999px;"><a href="{URL}" target="_blank" '
            f'style="{F}display:inline-block;padding:16px 32px;font-size:17px;font-weight:800;color:#ffffff;text-decoration:none;border-radius:999px;">{label}</a></td></tr></table>')

def h2(t, acc=''):
    a = f' <span style="{SER}font-weight:500;color:#c6a8f7;">{acc}</span>' if acc else ''
    return f'<p style="{F}font-size:24px;line-height:1.25;font-weight:800;color:#ffffff;margin:8px 0 14px 0;">{t}{a}</p>'

def signature(phone):
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="border-top:1px solid #3a2c55;margin-top:8px;"><tr><td style="padding:22px 0 0 0;">'
            f'<p style="{F}font-size:16px;line-height:1.5;color:#d9d3e6;margin:0 0 10px 0;">Pozdrawiam serdecznie</p>'
            f'<p style="{F}font-size:18px;font-weight:800;color:#ffffff;margin:0;">Natalia Słupianek</p>'
            f'<p style="{SER}font-size:16px;color:#c6a8f7;margin:2px 0 10px 0;">Event Manager · Avufu Event</p>'
            f'<p style="{F}font-size:14px;line-height:1.6;color:#aaa3bc;margin:0;"><a href="https://event.avufu.com" style="color:#ffffff;text-decoration:none;font-weight:700;">event.avufu.com</a> · {phone}</p>'
            f'</td></tr></table>')

def wrap(inner, preheader):
    return f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light"><title>Avufu Event</title></head>
<body style="margin:0;padding:0;background:#120c1d;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{preheader}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#120c1d" style="background:#120c1d;"><tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="#1a1129" style="width:600px;max-width:100%;background:#1a1129;border-radius:18px;overflow:hidden;">
<tr><td><a href="{URL}" target="_blank"><img src="{IMG}naglowek-wigilia-v2.jpg" width="600" alt="Avufu Event – Twoja przestrzeń. Wielkie wydarzenie." style="display:block;width:100%;max-width:600px;height:auto;border:0;"></a></td></tr>
<tr><td style="padding:34px 38px 36px 38px;">{inner}</td></tr>
</table>
<p style="{F}font-size:12px;line-height:1.5;color:#6f6886;margin:16px 0 0 0;">Avufu Event · Wrocław, Poznań i okolice · Odpowiadamy na Państwa zapytanie.</p>
</td></tr></table></body></html>'''

CONFIG_IMG = (f'<a href="{URL}" target="_blank"><img src="{IMG}konfigurator-wigilia-v2.jpg" width="524" alt="Konfigurator Wigilii – otwórz" '
              f'style="display:block;width:100%;max-width:524px;height:auto;border:0;border-radius:14px;margin:4px 0 20px 0;"></a>')

def odpowiedz(phone):
    i = p('Dzień dobry,')
    i += p('dziękuję za zainteresowanie firmową Wigilią z Avufu Event. Nazywam się Natalia Słupianek i będę Państwa opiekunką od pierwszej rozmowy aż do zakończenia wydarzenia.')
    i += p('Zajmujemy się oprawą wydarzeń firmowych we własnej przestrzeni klienta: w biurze, magazynie lub showroomie. Przywozimy światło, nagłośnienie i scenografię, prowadzimy wieczór i sprawiamy, że zwykłe biuro na kilka godzin staje się salą bankietową.', mb=22)
    i += h2('Dlaczego warto zrobić Wigilię', 'z nami?')
    i += bullets([('Bez wynajmu sali i dojazdu', 'zespół świętuje tam, gdzie już jest.'),
                  ('Jeden opiekun i jedna oferta', 'nie muszą Państwo koordynować kilku wykonawców.'),
                  ('Jasna cena', 'ofertę przygotowujemy w trzech wariantach, z opisanym zakresem, bez dopłat, o których nikt nie wspomniał.'),
                  ('Spokój w dniu wydarzenia', 'przed wyceną sprawdzamy zasilanie, wymiary i czas montażu, a sprzęt zapasowy planujemy z góry.')])
    i += h2('Ile może kosztować', 'Państwa Wigilia?')
    i += p('Najszybciej zrobią to Państwo w naszym konfiguratorze. Wystarczy kilka wyborów: liczba gości, poczęstunek, napoje, nagłośnienie, światło i obsługa.')
    i += CONFIG_IMG + button('Zaplanuj Wigilię w konfiguratorze')
    i += p('Warto zrobić to już teraz. Od 2025 roku 24 grudnia jest dniem wolnym od pracy, więc na firmowe spotkania zostaje w tym roku 17 dni roboczych (do 23 grudnia).')
    i += p(f'Po otrzymaniu konfiguracji skontaktuję się z propozycją krótkiej rozmowy lub wizji lokalnej. Wolą Państwo od razu porozmawiać? Wystarczy odpisać na tę wiadomość albo zadzwonić pod numer {phone}.', mb=24)
    i += signature(phone)
    return wrap(i, 'Firmowa Wigilia w Państwa biurze – bez wynajmu sali. Koszt sprawdzą Państwo w konfiguratorze.')

def przypomnienie(phone):
    i = p('Dzień dobry,')
    i += p('wracam do Państwa zapytania o firmową Wigilię. Grudzień szybko się zapełnia, dlatego przesyłam najprostszy sposób, by ruszyć z planowaniem.', mb=22)
    i += h2('Firmowa Wigilia', 'w kilku krokach')
    i += p('W konfiguratorze wybiorą Państwo liczbę gości, poczęstunek, napoje, nagłośnienie, światło i obsługę, a od razu zobaczą orientacyjny koszt wieczoru. Nic Państwa do niczego nie zobowiązuje.')
    i += CONFIG_IMG + button('Skonfiguruj Wigilię')
    i += p(f'Na podstawie konfiguracji przygotuję ofertę w trzech wariantach i zaproponuję termin wizji lokalnej. Jeśli wygodniej będzie porozmawiać, proszę odpisać albo zadzwonić pod numer {phone}.', mb=24)
    i += signature(phone)
    return wrap(i, 'Konfiguracja firmowej Wigilii – kilka wyborów i orientacyjny koszt od razu.')

if __name__ == '__main__':
    import sys
    phone = sys.argv[2] if len(sys.argv) > 2 else '[telefon]'
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    (out / 'mail-1-odpowiedz-na-zapytanie.html').write_text(odpowiedz(phone), encoding='utf-8')
    (out / 'mail-2-przypomnienie.html').write_text(przypomnienie(phone), encoding='utf-8')
    print('ok')
