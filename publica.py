#!/usr/bin/env python3
"""Prepara docs/, la carpeta que publica GitHub Pages.

    python3 publica.py                     # comprova i, si tot va bé, refresca docs/
    python3 publica.py --sense-comprovar   # salta la comprovació

Abans de copiar res passa la cadena sencera: aplica.py (estil, navegació i
enllaços), curriculum.py (blocs de currículum i matriu) i revisa.py. Si
revisa.py troba un error, no es publica.

Copia a docs/ el portal del mòdul, les pàgines de cada RA (índex, teoria,
guies i activitats) i les imatges de RAn/img. La resta del repositori —el
material d'origen de _aportacio/, la programació i les eines— no es copia.

GitHub Pages serveix docs/ des de la branca principal: executa'l abans de
cada git push i el web quedarà al dia.
"""
import os, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ROOT / 'docs'
CSS = ROOT / '_identitat' / 'sinapsi.css'
QUIZ = ROOT / '_identitat' / 'quiz.js'
FONTS = ROOT / '_identitat' / 'fonts'
FOLDERS = ('teoria', 'guies', 'activitats', 'practiques')

def ra_folders():
    return sorted(p for p in ROOT.glob('RA*') if p.is_dir())


FONTS_CSS = '''@font-face {
  font-family: "Ubuntu";
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url("fonts/ubuntu-500.ttf") format("truetype");
}
@font-face {
  font-family: "Ubuntu";
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url("fonts/ubuntu-700.ttf") format("truetype");
}
@font-face {
  font-family: "Source Sans 3";
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url("fonts/source-sans-3-400.ttf") format("truetype");
}
@font-face {
  font-family: "Source Sans 3";
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url("fonts/source-sans-3-600.ttf") format("truetype");
}
@font-face {
  font-family: "JetBrains Mono";
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url("fonts/jetbrains-mono-400.ttf") format("truetype");
}
@font-face {
  font-family: "JetBrains Mono";
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url("fonts/jetbrains-mono-500.ttf") format("truetype");
}
'''


def externalitza_web(docs, css=None, quiz=None, fonts=None):
    """Deixa la còpia pública amb recursos comuns, no les fonts de treball.

    Les pàgines del repositori privat continuen sent autocontingudes per a
    Moodle i per a l'editor. Aquesta transformació només s'aplica a docs/.
    """
    css = CSS.read_text(encoding='utf-8') if css is None else css
    quiz = QUIZ.read_text(encoding='utf-8') if quiz is None else quiz
    fonts = FONTS if fonts is None else fonts
    assets = docs / '_identitat'
    assets.mkdir(exist_ok=True)
    (assets / 'sinapsi.css').write_text(FONTS_CSS + '\n' + css, encoding='utf-8')
    (assets / 'quiz.js').write_text(quiz, encoding='utf-8')
    shutil.copytree(fonts, assets / 'fonts')

    copied = 0
    for page in docs.rglob('*.html'):
        src = page.read_text(encoding='utf-8')
        rel_assets = os.path.relpath(assets, page.parent).replace(os.sep, '/')
        src = re.sub(r'<style>.*?</style>',
                     f'<link rel="stylesheet" href="{rel_assets}/sinapsi.css">',
                     src, count=1, flags=re.S)
        src = re.sub(r'\s*<link\b[^>]*\bhref=["\']https://fonts\.(?:googleapis|gstatic)\.com[^"\']*["\'][^>]*>',
                     '', src)
        if '<main>' not in src:
            src = src.replace('<header class="cq-header">',
                              '<main>\n<header class="cq-header">', 1)
            close_at = src.find('<script')
            if close_at < 0:
                close_at = src.index('</body>')
            src = src[:close_at] + '</main>\n' + src[close_at:]
        src = re.sub(r'<script>.*?</script>',
                     f'<script src="{rel_assets}/quiz.js"></script>',
                     src, count=1, flags=re.S)
        page.write_text(src, encoding='utf-8')
        copied += 1
    return copied


def comprova():
    """Regenera el que és generat i verifica-ho. Si falla, no es publica."""
    for eina in (['Programación_didactica/curriculum.py', '--matriu'],
                 ['Programación_didactica/rubriques.py'],
                 ['aplica.py'],
                 ['revisa.py']):
        print(f'--- {eina[0]}', flush=True)
        r = subprocess.run([sys.executable] + eina, cwd=ROOT)
        if r.returncode != 0:
            sys.exit(f'\n{eina[0]} ha trobat problemes: no publico res.')


def main():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()

    copied = 0
    shutil.copy2(ROOT / 'index.html', DOCS / 'index.html')
    copied += 1

    for ra in ra_folders():
        out = DOCS / ra.name
        out.mkdir()
        if (ra / 'index.html').exists():
            shutil.copy2(ra / 'index.html', out / 'index.html')
            copied += 1
        if (ra / 'img').is_dir():
            shutil.copytree(ra / 'img', out / 'img')
        for folder in FOLDERS:
            src = ra / folder
            if not src.is_dir():
                continue
            (out / folder).mkdir()
            for page in sorted(src.glob('*.html')):
                shutil.copy2(page, out / folder / page.name)
                copied += 1

    # Evita que Pages passi les pàgines pel processador de plantilles Jekyll.
    (DOCS / '.nojekyll').write_text('', encoding='utf-8')
    externalitza_web(DOCS)

    print(f'OK  docs/  ·  {copied} pàgines  ·  '
          f'{", ".join(p.name for p in ra_folders())}')


if __name__ == '__main__':
    if '--sense-comprovar' not in sys.argv:
        comprova()
    main()
