"""Grafiki do maili Avufu Event (nagłówek + karta konfiguratora), w identyfikacji Event."""
import sys, pathlib, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generator import font_css, LOGO, typo
from playwright.sync_api import sync_playwright

BASE = """*{margin:0;padding:0;box-sizing:border-box}
body{width:%dpx;height:%dpx;background:#1a1129;color:#fff;font-family:'Manrope',sans-serif;overflow:hidden;position:relative}
.bg{position:absolute;inset:0;background:
 radial-gradient(ellipse 60%% 80%% at 95%% 0%%,rgba(110,66,180,.85),transparent 70%%),
 radial-gradient(ellipse 50%% 70%% at 0%% 100%%,rgba(36,40,92,.9),transparent 70%%),
 radial-gradient(ellipse 45%% 60%% at 100%% 100%%,rgba(80,36,56,.6),transparent 70%%)}
.wrap{position:relative;height:100%%;display:flex;flex-direction:column}
.logo{display:flex;align-items:center;gap:18px}.logo svg{width:84px}
.lw{line-height:1}.l1{font-weight:700;font-size:28px;color:#ddd7e8}.l1 i{font-style:normal;color:#a855f7}
.l2{font-weight:800;font-size:58px;letter-spacing:-1px}
.kicker{font-size:24px;font-weight:700;letter-spacing:.32em;text-transform:uppercase;color:#b98cff}
h1{font-weight:800;font-size:76px;line-height:1.05;letter-spacing:-1.5px}
h1 em{font-family:'Playfair Display';font-style:italic;font-weight:500;color:#c6a8f7}
p{font-size:30px;line-height:1.45;color:#aaa3bc}
.chips{display:flex;flex-wrap:wrap;gap:14px}
.chip{display:flex;align-items:center;gap:14px;font-size:27px;font-weight:600;color:#ece8f4;padding:14px 24px;border-radius:999px;
 background:rgba(255,255,255,.07);border:1px solid rgba(198,168,247,.28)}
.chip b{font-family:'Playfair Display';font-style:italic;font-weight:500;color:#c6a8f7;font-size:28px}
.btn{align-self:flex-start;font-weight:800;font-size:30px;background:#a855f7;color:#fff;padding:22px 40px;border-radius:999px}
"""

HEADER = f"""<div class="bg"></div><div class="wrap" style="padding:64px 76px;justify-content:space-between">{LOGO}
<div style="display:flex;flex-direction:column;gap:22px"><div class="kicker">Firmowa Wigilia w biurze</div>
<h1>Twoja przestrzeń.<br><em>Wielkie wydarzenie.</em></h1>
<p>{typo('Światło, dźwięk, scenografia i prowadzenie – Wrocław, Poznań i okolice.')}</p></div></div>"""

STEPS = ['Goście', 'Poczęstunek', 'Napoje', 'Nagłośnienie', 'Światło', 'Obsługa']
CONFIG = f"""<div class="bg"></div><div class="wrap" style="padding:60px 76px;gap:28px;justify-content:center">
<div class="kicker">Konfigurator Wigilii</div>
<h1 style="font-size:64px">Firmowa Wigilia <em>w kilku krokach</em></h1>
<div class="chips">{''.join(f'<div class="chip"><b>{i}</b>{s}</div>' for i, s in enumerate(STEPS, 1))}</div></div>"""

def shot(html, w, h, out):
    fonts = font_css()
    tmp = pathlib.Path(tempfile.mkdtemp()) / 'e.html'
    tmp.write_text(f'<!doctype html><html lang="pl"><head><meta charset="utf-8"><style>{fonts}{BASE % (w, h)}</style></head><body>{html}</body></html>', encoding='utf-8')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
        pg.goto(f'file://{tmp}'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(150)
        pg.screenshot(path=out, type='jpeg', quality=88); b.close()

if __name__ == '__main__':
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    shot(HEADER, 1200, 520, str(out / 'naglowek-wigilia.jpg'))
    shot(CONFIG, 1200, 440, str(out / 'konfigurator-wigilia.jpg'))
    print('ok')
