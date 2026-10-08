#!/usr/bin/env python3
"""Munta RAn/_identitat/raN-web.html: totes les pàgines d'un RA en una de
sola, navegable.

    python3 fes-web.py          # tots els RA
    python3 fes-web.py RA2      # només un RA

Serveix per revisar el material abans de pujar-lo a Moodle. Els fitxers de
teoria/, guies/, activitats/ i practiques/ són la font: aquest script no els modifica mai.
Tampoc modifica RAn/index.html: n'hi llegeix el bloc d'índex (referència,
títol i subtítol de cada pàgina) perquè la llista no es pugui desincronitzar
d'allò que ja es veu al portal del RA.

El llenç del document conserva la identitat SINAPSI exacta i es veu sempre en
clar, com el veurà l'alumnat. El marc de navegació (_identitat/web-marc.html,
compartit per tots els RA) és a part i s'adapta al tema de qui mira.
"""
import html, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
MARC = ROOT / '_identitat' / 'web-marc.html'

GROUPS = ('teoria', 'guies', 'activitats', 'practiques')

BLOCK_RE = re.compile(
    r'<div class="cq-block" data-kind="(' + '|'.join(GROUPS) + r')">(.*?)\n</div>', re.S)
ITEM_RE = re.compile(
    r'<a href="([^"]+)">\s*<span class="ref">([^<]*)</span>\s*'
    r'<span class="ttl">(.*?)<span class="sub">([^<]*)</span></span></a>', re.S)


def ra_folders():
    return sorted(p for p in ROOT.glob('RA*') if p.is_dir())


def index_pages(ra):
    """Llegeix RAn/index.html i en treu (h1, lede, pàgines).

    Cada pàgina és (pid, ref, títol, subtítol, grup, camí). El camí és
    relatiu a l'arrel del repositori. L'índex és l'única font: si hi falta
    una pàgina o hi ha un enllaç trencat, es descobreix aquí.
    """
    src = (ra / 'index.html').read_text(encoding='utf-8')
    h1 = re.search(r'<h1>(.*?)</h1>', src, re.S).group(1).strip()
    lede = re.search(r'<p class="lede">(.*?)</p>', src, re.S).group(1).strip()

    pages = []
    for group, body in BLOCK_RE.findall(src):
        for href, ref, ttl, sub in ITEM_RE.findall(body):
            title = re.sub(r'\s+', ' ', ttl).strip()
            pid = ref.lower().replace('.', '-')
            pages.append((pid, ref, title, sub.strip(), group, f'{ra.name}/{href}'))

    missing = [p for *_, p in pages if not (ROOT / p).exists()]
    if missing:
        sys.exit(f'{ra.name}: l\'índex enllaça pàgines que no existeixen: '
                 + ', '.join(missing))
    return h1, lede, pages


def neteja_cos(body):
    """Treu la navegació i el <main> propis d'una pàgina abans d'agregar-la."""
    body = re.sub(r'<!-- === (NAVEGACIÓ|PEU DE NAVEGACIÓ) INICI === -->.*?'
                  r'<!-- === \1 FI === -->\n?', '', body, flags=re.S).strip()
    if body.startswith('<main>') and body.endswith('</main>'):
        body = body[len('<main>'):-len('</main>')].strip()
    return body


def generate(ra):
    """Munta RAn/_identitat/raN-web.html. Retorna la línia de resum."""
    h1, lede, pages = index_pages(ra)
    if not pages:
        sys.exit(f'{ra.name}: l\'índex no enllaça cap pàgina.')

    src = (ROOT / pages[0][5]).read_text(encoding='utf-8')

    # La identitat s'encapsula a .sx-paper perquè no arribi al marc de navegació.
    ident = src[src.index('/* === SINAPSI-CSS INICI'):src.index('/* === SINAPSI-CSS FI')]
    assert ':root {' in ident and '\n  body {' in ident, 'la identitat ha canviat d\'estructura'
    ident = ident.replace(':root {', '.sx-paper {', 1).replace('\n  body {', '\n  .sx-paper {', 1)
    ident = ident.replace('.sx-paper {\n    margin: 0;\n    padding: 40px 16px 72px;',
                          '.sx-paper {\n    padding: 40px 22px 56px;')

    quiz_js = src[src.index('<script>') + len('<script>'):src.index('</script>')].strip()

    sections, nav = [], {g: [] for g in GROUPS}
    for pid, ref, title, sub, group, path in pages:
        t = (ROOT / path).read_text(encoding='utf-8')
        body = t[t.index('<body>') + len('<body>'):t.index('<script>')]
        # La navegació de la pàgina solta sobra aquí: la web ja té la seva.
        body = neteja_cos(body)
        sections.append(f'    <section class="sx-page" id="p-{pid}" hidden>\n'
                        f'      <div class="sx-paper">\n{body}\n      </div>\n    </section>')
        nav[group].append(
            f'        <li><button class="sx-nav-item" data-target="p-{pid}">'
            f'<span class="sx-ref">{ref}</span>'
            f'<span class="sx-nav-txt"><span class="sx-nav-ttl">{html.escape(title)}</span>'
            f'<span class="sx-nav-sub">{html.escape(sub)}</span></span></button></li>')

    page = MARC.read_text(encoding='utf-8')
    for marker, value in [('<!--IDENTITAT-->', ident),
                          ('<!--ARIA_LABEL-->', f'Pàgines del {ra.name}'),
                          ('<!--RA_H1-->', html.escape(h1)),
                          ('<!--RA_LEDE-->', html.escape(lede)),
                          ('<!--NAV_TEORIA-->', '\n'.join(nav['teoria'])),
                          ('<!--NAV_GUIES-->', '\n'.join(nav['guies'])),
                          ('<!--NAV_ACTIVITATS-->', '\n'.join(nav['activitats'])),
                          ('<!--NAV_PRACTIQUES-->', '\n'.join(nav['practiques'])),
                          ('<!--SECCIONS-->', '\n\n'.join(sections)),
                          ('<!--QUIZ-->', quiz_js)]:
        assert marker in page, f'falta el marcador {marker} a web-marc.html'
        page = page.replace(marker, value)

    out = ra / '_identitat' / f'{ra.name.lower()}-web.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding='utf-8')
    return f'OK  {out.relative_to(ROOT)}  ·  {len(sections)} pàgines  ·  {out.stat().st_size // 1024} KB'


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    ras = [ra for ra in ra_folders() if not only or ra.name == only]
    if not ras:
        sys.exit(f'No he trobat cap RA{" anomenat " + only if only else ""}.')
    for ra in ras:
        print(generate(ra))


if __name__ == '__main__':
    main()
