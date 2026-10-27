"""Szablony maili Avufu Event, wersja 2: tekst w HTML (działa bez obrazków), akcenty marki w CSS.
Jedyny obrazek to mały znak ^ w nagłówku – bez niego mail wygląda tak samo, tylko bez znaku.
Użycie: python3 build_email.py katalog_wyjsciowy [telefon]
"""
import pathlib, sys
IMG = 'https://raw.githubusercontent.com/dawidsbrzozowski/avufu-event-social/main/social/email/'
URL = 'https://event.avufu.com/firmowa-wigilia.html'
SANS = "font-family:Manrope,'Segoe UI',Helvetica,Arial,sans-serif;"
SERIF = "font-family:'Playfair Display',Georgia,'Times New Roman',serif;font-style:italic;font-weight:500;"
INK, SOFT, VIO, LAV = '#241a38', '#4a4160', '#7c3aed', '#c6a8f7'
GRAD_DARK = 'background-color:#1f1433;background-image:linear-gradient(135deg,#3b2468 0%,#1f1433 55%,#2a1830 100%);'
GRAD_BOX = 'background-color:#2c1b4f;background-image:linear-gradient(135deg,#4a2c86 0%,#2c1b4f 60%,#1f1433 100%);'

def p(t, mb=16, color=SOFT, size=16):
    return f'<p style="{SANS}font-size:{size}px;line-height:1.65;color:{color};margin:0 0 {mb}px 0;">{t}</p>'

def h2(t, acc):
    return (f'<p style="{SANS}font-size:23px;line-height:1.3;font-weight:800;color:{INK};margin:10px 0 14px 0;">{t} '
            f'<span style="{SERIF}color:{VIO};">{acc}</span></p>')

def bullets(items):
    rows = ''.join(
        f'<tr><td valign="top" width="22" style="{SERIF}font-size:20px;line-height:1.4;color:{VIO};padding:0 0 12px 0;">–</td>'
        f'<td style="{SANS}font-size:16px;line-height:1.6;color:{SOFT};padding:0 0 12px 0;"><strong style="color:{INK};">{a}</strong> – {b}</td></tr>'
        for a, b in items)
    return f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 10px 0;">{rows}</table>'

def button(label, bg='#a855f7', color='#ffffff'):
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 4px 0;"><tr>'
            f'<td bgcolor="{bg}" style="border-radius:999px;background:{bg};">'
            f'<a href="{URL}" target="_blank" style="{SANS}display:inline-block;padding:15px 30px;font-size:16px;font-weight:800;'
            f'color:{color};text-decoration:none;border-radius:999px;">{label} &rarr;</a></td></tr></table>')

def chips():
    steps = ['Goście', 'Poczęstunek', 'Napoje', 'Nagłośnienie', 'Światło', 'Obsługa']
    return ''.join(
        f'<span style="display:inline-block;margin:0 6px 8px 0;padding:7px 14px;border-radius:999px;border:1px solid rgba(198,168,247,.45);'
        f'{SANS}font-size:14px;font-weight:600;color:#ece8f4;white-space:nowrap;"><span style="{SERIF}color:{LAV};">{i}</span>&nbsp; {s}</span>'
        for i, s in enumerate(steps, 1))

def config_box(title, acc, text, label):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:18px 0 24px 0;"><tr>'
            f'<td bgcolor="#2c1b4f" style="{GRAD_BOX}border-radius:16px;padding:26px 26px 24px 26px;">'
            f'<p style="{SANS}font-size:12px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:{LAV};margin:0 0 10px 0;">Konfigurator Wigilii</p>'
            f'<p style="{SANS}font-size:22px;line-height:1.3;font-weight:800;color:#ffffff;margin:0 0 10px 0;">{title} <span style="{SERIF}color:{LAV};">{acc}</span></p>'
            f'<p style="{SANS}font-size:15px;line-height:1.6;color:#d9d3e6;margin:0 0 14px 0;">{text}</p>'
            f'<div style="margin:0 0 12px 0;">{chips()}</div>{button(label)}</td></tr></table>')

def header():
    return (f'<tr><td bgcolor="#1f1433" style="{GRAD_DARK}padding:28px 36px 30px 36px;">'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td valign="middle" style="padding-right:12px;"><img src="{IMG}znak-avufu-event.png" width="44" height="33" alt="" style="display:block;border:0;"></td>'
            f'<td valign="middle" style="{SANS}line-height:1;"><span style="font-size:14px;font-weight:700;color:#ddd7e8;">avufu<span style="color:#a855f7;">.</span></span><br>'
            f'<span style="font-size:28px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">EVENT</span></td></tr></table>'
            f'<p style="{SANS}font-size:12px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#b98cff;margin:22px 0 8px 0;">Firmowa Wigilia w biurze</p>'
            f'<p style="{SANS}font-size:30px;line-height:1.15;font-weight:800;color:#ffffff;margin:0;">Twoja przestrzeń.<br>'
            f'<span style="{SERIF}font-size:32px;color:{LAV};">Wielkie wydarzenie.</span></p></td></tr>')

def signature(phone):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid #e6e0f0;margin-top:10px;">'
            f'<tr><td style="padding:22px 0 0 0;">{p("Pozdrawiam serdecznie", mb=10)}'
            f'<p style="{SANS}font-size:17px;font-weight:800;color:{INK};margin:0;">Natalia Słupianek</p>'
            f'<p style="{SERIF}font-size:15px;color:{VIO};margin:2px 0 8px 0;">Event Manager · Avufu Event</p>'
            f'<p style="{SANS}font-size:14px;line-height:1.6;color:{SOFT};margin:0;"><a href="https://event.avufu.com" style="color:{INK};font-weight:700;text-decoration:none;">event.avufu.com</a> · {phone}</p>'
            f'</td></tr></table>')

def wrap(inner, preheader):
    return f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Playfair+Display:ital,wght@1,500&display=swap" rel="stylesheet">
<title>Avufu Event</title></head>
<body style="margin:0;padding:0;background:#f4f1fa;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{preheader}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f4f1fa"><tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="width:600px;max-width:100%;background:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e6e0f0;">
{header()}
<tr><td style="padding:32px 36px 34px 36px;">{inner}</td></tr>
</table>
<p style="{SANS}font-size:12px;line-height:1.5;color:#8a83a0;margin:14px 0 0 0;">Avufu Event · Wrocław, Poznań i okolice · Wiadomość w odpowiedzi na Państwa zapytanie.</p>
</td></tr></table></body></html>'''

def odpowiedz(phone):
    i = p('Dzień dobry,')
    i += p('dziękuję za zainteresowanie firmową Wigilią z Avufu Event. Nazywam się Natalia Słupianek i będę Państwa opiekunką od pierwszej rozmowy aż do zakończenia wydarzenia.')
    i += p('Zajmujemy się oprawą wydarzeń firmowych we własnej przestrzeni klienta: w biurze, magazynie lub showroomie. Przywozimy światło, nagłośnienie i scenografię, prowadzimy wieczór i sprawiamy, że zwykłe biuro na kilka godzin staje się salą bankietową.', mb=20)
    i += h2('Dlaczego warto zrobić Wigilię', 'z nami?')
    i += bullets([('Bez wynajmu sali i dojazdu', 'zespół świętuje tam, gdzie już jest.'),
                  ('Jeden opiekun i jedna oferta', 'nie muszą Państwo koordynować kilku wykonawców.'),
                  ('Jasna cena', 'ofertę przygotowujemy w trzech wariantach, z opisanym zakresem, bez dopłat, o których nikt nie wspomniał.'),
                  ('Spokój w dniu wydarzenia', 'przed wyceną sprawdzamy zasilanie, wymiary i czas montażu, a sprzęt zapasowy planujemy z góry.')])
    i += config_box('Ile może kosztować', 'Państwa Wigilia?',
                    'Najszybciej sprawdzą to Państwo w naszym konfiguratorze. Wystarczy kilka wyborów, a orientacyjny koszt wieczoru pojawi się od razu.',
                    'Zaplanuj Wigilię w konfiguratorze')
    i += p('Warto zrobić to już teraz. Od 2025 roku 24 grudnia jest dniem wolnym od pracy, więc na firmowe spotkania zostaje w tym roku <strong style="color:#241a38;">17 dni roboczych</strong> (do 23 grudnia).')
    i += p(f'Po otrzymaniu konfiguracji skontaktuję się z propozycją krótkiej rozmowy lub wizji lokalnej. Wolą Państwo od razu porozmawiać? Wystarczy odpisać na tę wiadomość albo zadzwonić pod numer {phone}.', mb=22)
    i += signature(phone)
    return wrap(i, 'Firmowa Wigilia w Państwa biurze – bez wynajmu sali. Koszt sprawdzą Państwo w konfiguratorze.')

def przypomnienie(phone):
    i = p('Dzień dobry,')
    i += p('wracam do Państwa zapytania o firmową Wigilię. Grudzień szybko się zapełnia, dlatego przesyłam najprostszy sposób, by ruszyć z planowaniem.')
    i += config_box('Firmowa Wigilia', 'w kilku krokach',
                    'Wybiorą Państwo liczbę gości, poczęstunek, napoje, nagłośnienie, światło i obsługę, a od razu zobaczą orientacyjny koszt wieczoru. Nic Państwa do niczego nie zobowiązuje.',
                    'Skonfiguruj Wigilię')
    i += p(f'Na podstawie konfiguracji przygotuję ofertę w trzech wariantach i zaproponuję termin wizji lokalnej. Jeśli wygodniej będzie porozmawiać, proszę odpisać albo zadzwonić pod numer {phone}.', mb=22)
    i += signature(phone)
    return wrap(i, 'Konfiguracja firmowej Wigilii – kilka wyborów i orientacyjny koszt od razu.')

if __name__ == '__main__':
    phone = sys.argv[2] if len(sys.argv) > 2 else '[telefon]'
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    (out / 'mail-1-odpowiedz-na-zapytanie.html').write_text(odpowiedz(phone), encoding='utf-8')
    (out / 'mail-2-przypomnienie.html').write_text(przypomnienie(phone), encoding='utf-8')
    print('ok')
