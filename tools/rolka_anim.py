"""Animowana rolka Avufu Event: tło delikatnie się przybliża, napisy wjeżdżają osobno, znak „?” na koniec podskakuje.
Użycie: python3 rolka_anim.py spec_rolki.json plik.mp4
Każdy post w specyfikacji = jedna scena (format story, 1 slajd). Klatki renderuje Chromium, wideo składa ffmpeg.
"""
import json, sys, pathlib, subprocess, tempfile, shutil
from playwright.sync_api import sync_playwright
from generator import slide_html, font_css

FPS, SCENE, FADE = 30, 4.125, 0.5          # 4 sceny x 4,125 s - 3 x 0,5 s przenikania = 15 s

ANIM = """
@keyframes zoom{from{transform:scale(1)}to{transform:scale(1.07)}}
@keyframes inUp{from{opacity:0;transform:translateY(70px)}to{opacity:1;transform:none}}
@keyframes hop{0%%,100%%{transform:translateY(0)}30%%{transform:translateY(-34px) rotate(-6deg)}55%%{transform:translateY(0)}75%%{transform:translateY(-12px)}}
.ph,.bg{animation:zoom %(d)ss linear both;transform-origin:60%% 45%%}
.main>*{animation:inUp .7s cubic-bezier(.2,.8,.2,1) both}
.main>*:nth-child(1){animation-delay:.25s}.main>*:nth-child(2){animation-delay:.5s}
.main>*:nth-child(3){animation-delay:.85s}.main>*:nth-child(4){animation-delay:1.1s}
.q{display:inline-block;animation:hop .55s ease-out both;animation-delay:%(q)ss}
"""

def scene_html(s, theme, fonts):
    h = slide_html(s, 1080, 1920, 1, 1, theme, fonts)
    h = h.replace('<div style="position:absolute;inset:0;background:url(', '<div class="ph" style="position:absolute;inset:0;background:url(', 1)
    # „?” tylko w tytule
    a, b = h.split('<h1>', 1); t, c = b.split('</h1>', 1)
    h = a + '<h1>' + t.replace('?', '<span class="q">?</span>') + '</h1>' + c
    return h.replace('</style>', ANIM % dict(d=SCENE, q=SCENE - 1.25) + '</style>', 1)

def main(spec, out):
    posts = json.loads(pathlib.Path(spec).read_text(encoding='utf-8'))['posts']
    tmp = pathlib.Path(tempfile.mkdtemp()); fonts = font_css(); clips = []
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={'width': 1080, 'height': 1920})
        for n, post in enumerate(posts):
            d = tmp / f's{n}'; d.mkdir()
            f = tmp / f's{n}.html'; f.write_text(scene_html(post['slides'][0], post.get('theme', 'dark'), fonts), encoding='utf-8')
            pg.goto(f'file://{f}'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(200)
            for i in range(int(SCENE * FPS)):
                pg.evaluate(f'document.getAnimations().forEach(a=>{{a.pause();a.currentTime={i * 1000 / FPS}}})')
                pg.screenshot(path=str(d / f'{i:04d}.jpg'), type='jpeg', quality=92)
            c = tmp / f's{n}.mp4'
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', str(d / '%04d.jpg'),
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', str(c)], check=True)
            clips.append(c)
        br.close()
    args, fc, last = [], '', '0:v'
    for c in clips: args += ['-i', str(c)]
    for k in range(1, len(clips)):
        lab = f'x{k}'; fc += f'[{last}][{k}:v]xfade=transition=fade:duration={FADE}:offset={k * (SCENE - FADE)}[{lab}];'; last = lab
    total = len(clips) * SCENE - (len(clips) - 1) * FADE
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *args, '-f', 'lavfi', '-t', str(total), '-i', 'anullsrc=r=44100:cl=stereo',
                    '-filter_complex', fc.rstrip(';'), '-map', f'[{last}]', '-map', f'{len(clips)}:a', '-c:v', 'libx264',
                    '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', '-movflags', '+faststart', out], check=True)
    shutil.rmtree(tmp)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
