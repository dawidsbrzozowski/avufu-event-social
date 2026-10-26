"""Generator grafik Avufu Event (IG/FB), wersja 3 – identyfikacja wizualna Avufu Event.
Użycie: python3 generator.py tresc.json katalog_wyjsciowy
Czcionki: Manrope (tekst) + Playfair Display italic (akcent), z paczek @fontsource w ./fonts.
Pola slajdu: kicker, num, title (*akcent kursywą*), text, list, olist (+start), rows [[etykieta, tekst]],
stats [[liczba, opis]], note, cta, source (przypis), size (rozmiar tytułu).
Pola posta: id, theme ("dark" | "violet"), format ("story" = 1080x1920, domyślnie 1080x1350).
"""
import json, sys, html, pathlib, re, tempfile
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
FONTS = ROOT / 'fonts'

def font_css():
    css = ''
    for pkg, files in [('fontsource-manrope-5.1.0', ['300', '400', '500', '600', '700', '800']),
                       ('fontsource-playfair-display-5.1.0', ['400-italic', '500-italic'])]:
        base = FONTS / pkg
        for f in files:
            t = (base / f'{f}.css').read_text()
            css += t.replace('url(./files/', f'url(file://{base}/files/')
    return css

LOGO = '''<div class="logo"><svg viewBox="0 0 64 48"><defs><linearGradient id="m" x1="0" y1="0" x2="1" y2="1">
<stop offset="0%" stop-color="#9b4cf5"/><stop offset="55%" stop-color="#a95ef6"/><stop offset="100%" stop-color="#d2b4fb"/></linearGradient></defs>
<path d="M12 40 L27 13 Q32 5 37 13 L52 40" fill="none" stroke="url(#m)" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>
<div class="lw"><div class="l1">avufu<i>.</i></div><div class="l2">EVENT</div></div></div>'''

THEMES = {
    'dark':   dict(bg='#1a1129', g1='rgba(88,52,150,.75)', g2='rgba(36,40,92,.85)', g3='rgba(70,34,48,.55)', card='rgba(255,255,255,.05)'),
    'violet': dict(bg='#3b2468', g1='rgba(150,96,230,.9)', g2='rgba(70,52,150,.85)', g3='rgba(120,60,120,.55)', card='rgba(255,255,255,.09)'),
}

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:%(w)dpx;height:%(h)dpx;background:%(bg)s;color:#fff;font-family:'Manrope',sans-serif;overflow:hidden;position:relative}
.bg{position:absolute;inset:0;background:
 radial-gradient(ellipse 70%% 55%% at 92%% 4%%,%(g1)s,transparent 70%%),
 radial-gradient(ellipse 60%% 45%% at 0%% 100%%,%(g2)s,transparent 70%%),
 radial-gradient(ellipse 55%% 40%% at 100%% 100%%,%(g3)s,transparent 70%%)}
.wrap{position:relative;height:100%%;padding:84px 82px 78px;display:flex;flex-direction:column}
.logo{display:flex;align-items:center;gap:20px}
.logo svg{width:92px;height:auto}
.lw{line-height:1}.l1{font-weight:700;font-size:31px;color:#ddd7e8;margin-left:2px;margin-bottom:-2px}.l1 i{font-style:normal;color:#a855f7}
.l2{font-weight:800;font-size:64px;letter-spacing:-1px;color:#fff}
.main{flex:1;display:flex;flex-direction:column;justify-content:center;gap:30px}
.kicker{font-size:25px;font-weight:700;letter-spacing:.32em;text-transform:uppercase;color:#b98cff}
h1{font-weight:800;font-size:%(h1)dpx;line-height:1.08;letter-spacing:-1.5px;color:#fff}
h1 em,.acc{font-family:'Playfair Display',serif;font-style:italic;font-weight:500;color:#c6a8f7;letter-spacing:-.5px}
p{font-size:37px;line-height:1.45;font-weight:400;color:#aaa3bc}
.num{font-family:'Playfair Display',serif;font-style:italic;font-weight:500;font-size:150px;line-height:1;color:#c6a8f7}
ul{list-style:none;display:flex;flex-direction:column;gap:20px}
li{font-size:35px;line-height:1.38;padding-left:40px;position:relative;color:#e9e4f2;font-weight:500}
li:before{content:'';position:absolute;left:2px;top:17px;width:12px;height:12px;border-radius:50%%;background:#a855f7;box-shadow:0 0 0 5px rgba(168,85,247,.22)}
ol{list-style:none;display:flex;flex-direction:column;gap:24px;counter-reset:n var(--start)}
ol li{padding-left:80px}
ol li:before{counter-increment:n;content:counter(n);width:54px;height:54px;top:-6px;left:0;border-radius:50%%;box-shadow:none;
 background:transparent;border:2px solid #a855f7;font-family:'Playfair Display';font-style:italic;font-size:30px;color:#c6a8f7;
 display:flex;align-items:center;justify-content:center}
.rows{display:flex;flex-direction:column;gap:16px}
.row{display:grid;grid-template-columns:170px 1fr;gap:22px;padding:24px 28px;border-radius:18px;background:%(card)s;border:1px solid rgba(198,168,247,.18)}
.row b{font-size:23px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#b98cff;padding-top:7px}
.row span{font-size:33px;line-height:1.38;color:#ece8f4}
.stats{display:flex;flex-direction:column;gap:24px}
.stat{display:flex;align-items:baseline;gap:28px;padding-bottom:22px;border-bottom:1px solid rgba(198,168,247,.18)}
.stat .v{font-family:'Playfair Display',serif;font-style:italic;font-weight:500;font-size:88px;line-height:1;color:#c6a8f7;white-space:nowrap}
.stat .d{font-size:32px;line-height:1.38;color:#cfc8dc}
.note{font-size:33px;line-height:1.45;padding:28px 32px;border-left:4px solid #a855f7;background:%(card)s;border-radius:0 18px 18px 0;color:#ece8f4}
.cta{align-self:flex-start;font-weight:700;font-size:32px;color:#fff;background:#a855f7;padding:22px 40px;border-radius:999px}
.src{font-size:21px;line-height:1.45;color:#8e87a3;margin-bottom:24px}
.foot{display:flex;justify-content:space-between;align-items:flex-end}
.tags{font-size:25px;font-weight:600;color:#cfc8dc;margin-bottom:12px}
.url{font-size:31px;font-weight:700;color:#fff}
.page{font-family:'Playfair Display';font-style:italic;font-size:30px;color:#b98cff}
"""

SHORT = re.compile(r'(?<![\w])((?:[wzioauWZIOAU])|(?:we|ze|do|na|od|po|za|że|bo|by)) ')
def typo(t):
    t = SHORT.sub(lambda m: m.group(1) + '\u00a0', t)
    return re.sub(r'(\d) (?=\S)', '\\1\u00a0', t)

def esc(t):
    t = html.escape(typo(t))
    parts = t.split('*')
    return ''.join(f'<em>{s}</em>' if i % 2 else s for i, s in enumerate(parts)).replace('\n', '<br>')

def slide_html(s, w, h, page, total, theme, fonts):
    b = ''
    if s.get('kicker'): b += f'<div class="kicker">{esc(s["kicker"])}</div>'
    if s.get('num'): b += f'<div class="num">{esc(s["num"])}</div>'
    if s.get('title'): b += f'<h1>{esc(s["title"])}</h1>'
    if s.get('text'): b += f'<p>{esc(s["text"])}</p>'
    if s.get('list'): b += '<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in s['list']) + '</ul>'
    if s.get('olist'):
        b += f'<ol style="--start:{s.get("start", 1) - 1}">' + ''.join(f'<li>{esc(x)}</li>' for x in s['olist']) + '</ol>'
    if s.get('rows'):
        b += '<div class="rows">' + ''.join(f'<div class="row"><b>{esc(a)}</b><span>{esc(c)}</span></div>' for a, c in s['rows']) + '</div>'
    if s.get('stats'):
        b += '<div class="stats">' + ''.join(f'<div class="stat"><div class="v">{esc(a)}</div><div class="d">{esc(c)}</div></div>' for a, c in s['stats']) + '</div>'
    if s.get('note'): b += f'<div class="note">{esc(s["note"])}</div>'
    if s.get('cta'): b += f'<div class="cta">{esc(s["cta"])}</div>'
    src = f'<div class="src">{esc(s["source"])}</div>' if s.get('source') else ''
    tags = f'<div class="tags">{esc(s["tags"])}</div>' if s.get('tags') else ''
    pg = f'<div class="page">{page}/{total}</div>' if total > 1 else '<div></div>'
    title = s.get('title', '')
    h1 = s.get('size', 96 if len(title) < 30 else 84 if len(title) < 50 else 72)
    css = CSS % dict(THEMES[theme], w=w, h=h, h1=h1)
    return f'''<!doctype html><html lang="pl"><head><meta charset="utf-8"><style>{fonts}{css}</style></head>
<body><div class="bg"></div><div class="wrap">{LOGO}
<div class="main">{b}</div>{src}
<div class="foot"><div>{tags}<div class="url">event.avufu.com</div></div>{pg}</div></div></body></html>'''

def render(spec_path, out_dir):
    spec = json.loads(pathlib.Path(spec_path).read_text(encoding='utf-8'))
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    fonts = font_css(); files = []
    tmp = pathlib.Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        br = p.chromium.launch()
        for post in spec['posts']:
            w, h = (1080, 1920) if post.get('format') == 'story' else (1080, 1350)
            pg = br.new_page(viewport={'width': w, 'height': h})
            n = len(post['slides'])
            for i, s in enumerate(post['slides'], 1):
                f = tmp / 'slide.html'
                f.write_text(slide_html(s, w, h, i, n, post.get('theme', 'dark'), fonts), encoding='utf-8')
                pg.goto(f'file://{f}'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(150)
                o = out / f"{post['id']}_{i:02d}.jpg"
                pg.screenshot(path=str(o), type='jpeg', quality=90); files.append(o)
            pg.close()
        br.close()
    return files

if __name__ == '__main__':
    for f in render(sys.argv[1], sys.argv[2]): print(f)
