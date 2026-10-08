#!/usr/bin/env python3
"""Revisa totes les pàgines del mòdul abans de publicar-les.

    python3 revisa.py          # totes
    python3 revisa.py RA2      # només un RA

Comprova el que s'ha de complir sempre:

  · el bloc CSS és idèntic byte a byte a totes les pàgines
  · no hi ha etiquetes mal tancades
  · cap data-id de test repetit dins de tot el mòdul
  · els quizzes tenen id, tipus, opcions, botó, feedback i respostes coherents
  · totes les taules van dins d'un .cq-tablewrap
  · cap línia de codi passa de 78 caràcters
  · cap enllaç intern apunta a una pàgina que no existeix
  · cap guia amb test i cap teoria ni activitat amb «pas a pas»
  · cap teoria amb fuga de producte (wp-config.php, php.ini, sudo…)
  · cap URL solta fora d'un <a> i cap títol de bloc que no sigui <h2>
  · totes les teories, activitats i pràctiques tenen el bloc de currículum
    (menys les del RA extra, que no és al currículum oficial)
  · avisa dels blocs d'explicació de més de 135 mots (regla de densitat)

Surt amb codi 1 si hi ha errors, perquè es pugui encadenar amb publica.py.
"""
import collections, hashlib, html, html.parser, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
MAX_LINE = 78
MAX_WORDS = 135

# La regla de densitat val per als blocs d'explicació. Les guies pas a pas,
# els problemes i els resums són llistes: allargar-se hi és normal.
DENSE = {'teoria', 'referència', 'exemple', 'cas real', 'escenari',
         'observació', 'recordatori'}

# Noms que només poden sortir a una guia: si apareixen a una teoria, la
# teoria ha deixat d'explicar el concepte i ha començat a explicar un
# producte concret (fitxers de configuració i ordres d'instal·lació).
PRODUCTE = ('wp-config.php', 'config.inc.php', 'php.ini', 'sites-available',
            'a2ensite', 'apt install', 'sudo ', 'mysql -u', 'occ ')

# RA complementaris, fora del currículum oficial.
EXTRA = {'RAX'}

# Excepcions revisades una a una, no per comoditat.
PRODUCTE_PERMES = set()


class Tags(html.parser.HTMLParser):
    VOID = {'br', 'img', 'meta', 'link', 'input', 'hr', 'source'}

    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1][0] != tag:
            self.errors.append(f'</{tag}> inesperat a la línia {self.getpos()[0]}')
        else:
            self.stack.pop()


OPEN_QUESTION = re.compile(r'<div class="cq-question"([^>]*)>')
DIV_TAG = re.compile(r'</?div\b')


def quiz_errors(src):
    """Valida l'estructura funcional de cada pregunta i retorna errors i ids."""
    errors, ids = [], []
    for start in OPEN_QUESTION.finditer(src):
        depth, pos, end = 1, start.end(), None
        while depth:
            tag = DIV_TAG.search(src, pos)
            if not tag:
                break
            depth += -1 if tag.group().startswith('</') else 1
            pos = tag.end()
            if depth == 0:
                end = tag.start()
        attrs = start.group(1)
        body = src[start.end():end] if end is not None else src[start.end():]
        qid_m = re.search(r'\bdata-id="([^"]+)"', attrs)
        qid = qid_m.group(1) if qid_m else '?'
        if qid_m:
            ids.append(qid)
        else:
            errors.append('pregunta sense data-id: ?')

        type_m = re.search(r'\bdata-type="([^"]+)"', attrs)
        qtype = type_m.group(1) if type_m else None
        if qtype not in ('single', 'multi'):
            errors.append(f'pregunta {qid}: data-type invàlid o absent')

        options = re.findall(
            r'<button\b(?=[^>]*\bclass="[^"]*\bcq-option\b[^"]*")([^>]*)>',
            body)
        if not options:
            errors.append(f'pregunta {qid}: no té opcions')
        correct = 0
        for n, option in enumerate(options, 1):
            value = re.search(r'\bdata-correct="([^"]+)"', option)
            if not value or value.group(1) not in ('true', 'false'):
                errors.append(f'pregunta {qid}: opció {n} sense data-correct vàlid')
            elif value.group(1) == 'true':
                correct += 1
        if qtype == 'single' and correct != 1:
            errors.append(f'pregunta {qid}: single amb {correct} respostes correctes')
        elif qtype == 'multi' and correct < 1:
            errors.append(f'pregunta {qid}: multi sense resposta correcta')

        if not re.search(r'\bclass="[^"]*\bcq-check-btn\b', body):
            errors.append(f'pregunta {qid}: falta el botó de comprovació')
        if not re.search(r'\bclass="[^"]*\bcq-feedback\b', body):
            errors.append(f'pregunta {qid}: falta el feedback')
    return errors, ids


def pages(only=None):
    found = []
    for ra in sorted(p for p in ROOT.glob('RA*') if p.is_dir()):
        if only and ra.name != only:
            continue
        if (ra / 'index.html').exists():
            found.append(ra / 'index.html')
        for folder in ('teoria', 'guies', 'activitats', 'practiques'):
            found += sorted((ra / folder).glob('*.html'))
    if not only and (ROOT / 'index.html').exists():
        found.append(ROOT / 'index.html')
    return found


def sense_div(fragment, classe):
    """Treu els <div class="classe"> amb tot el que contenen, comptant els
    <div> imbricats. Serveix per als diagrames, que tenen divs a dins."""
    out, i = [], 0
    obre = re.compile(r'<div class="' + re.escape(classe) + r'"')
    while True:
        m = obre.search(fragment, i)
        if not m:
            out.append(fragment[i:])
            return ''.join(out)
        out.append(fragment[i:m.start()])
        nivell, j = 0, m.start()
        for tag in re.finditer(r'<div\b|</div>', fragment[m.start():]):
            nivell += 1 if tag.group() == '<div' else -1
            if nivell == 0:
                j = m.start() + tag.end()
                break
        i = j


def text_of(fragment):
    """Text visible d'un fragment: només la prosa.

    En queden fora el codi, les taules, els diagrames i el test. El que és
    enumerable ha d'anar en taula o en llista (regla de densitat de la GUIA),
    i comptar-ho com a prosa penalitzaria justament fer-ho bé."""
    f = re.sub(r'<(pre|table|script)\b.*?</\1>', ' ', fragment, flags=re.S)
    f = re.sub(r'<div class="cq-question".*', ' ', f, flags=re.S)
    f = sense_div(f, 'dora-flow')
    return html.unescape(re.sub(r'<[^>]+>', ' ', f))


def cos(src):
    """El contingut real de la pàgina: sense el <head>, l'estil ni els
    scripts. El CSS comú porta els noms de tots els data-kind, i buscar-hi
    res donaria un positiu a totes les pàgines."""
    c = src[src.index('<body'):] if '<body' in src else src
    return re.sub(r'<(script|style)\b.*?</\1>', ' ', c, flags=re.S)


def sense_codi(src):
    """El cos sense el codi: el que queda és prosa escrita per a l'alumnat."""
    c = re.sub(r'<pre\b.*?</pre>', ' ', cos(src), flags=re.S)
    return re.sub(r'<code\b.*?</code>', ' ', c, flags=re.S)


def estructura(path, src):
    """Les regles que depenen del tipus de pàgina: teoria, guia o activitat."""
    tipus = path.parent.name
    errors = []
    c = cos(src)

    te_test = 'cq-question' in c
    te_passos = 'data-kind="pas a pas"' in c
    te_curriculum = 'data-kind="currículum"' in c

    if tipus == 'guies':
        if te_test:
            errors.append('una guia no porta test')
    elif tipus in ('teoria', 'activitats', 'practiques'):
        if te_passos:
            errors.append(f'un «pas a pas» fora d\'una guia ({tipus})')
        # El RA extra no és al currículum oficial: no porta aquest bloc.
        if not te_curriculum and path.parent.parent.name not in EXTRA:
            errors.append('falta el bloc de currículum: dona-la d\'alta a '
                          'MAP de Programación_didactica/curriculum.py')

    if tipus == 'teoria' and path.name not in PRODUCTE_PERMES:
        # El test queda fora: pregunta sobre el que es fa a la guia, i
        # anomenar-hi una directiva és la gràcia de la pregunta.
        sense_test = re.sub(r'<div class="cq-question".*', ' ', c, flags=re.S)
        for nom in PRODUCTE:
            if nom in sense_test:
                errors.append(f'fuga de producte a una teoria: {nom}')

    return errors


def enllacos(path, src):
    """Enllaços interns que apunten a una pàgina que no existeix."""
    errors = []
    # El codi d'exemple (HTML dins de <pre> o <code>) no són enllaços reals.
    sense = re.sub(r'<(pre|code)\b.*?</\1>', ' ', src, flags=re.S)
    for href in re.findall(r'(?:href|src)="([^"]+)"', sense):
        if href.startswith(('http://', 'https://', 'mailto:', '#', 'data:')):
            continue
        desti = (path.parent / href.split('#')[0]).resolve()
        if not desti.exists():
            errors.append(f'enllaç trencat: {href}')
    return errors


def check(path):
    """Retorna (errors, avisos, hash del CSS, data-ids) d'una pàgina."""
    src = path.read_text(encoding='utf-8')
    errors, warnings = [], []

    errors += estructura(path, src)
    errors += enllacos(path, src)

    prosa = sense_codi(src)
    for url in re.findall(r'(?<!["\w])(https?://[^\s<)"]+)', prosa):
        errors.append(f'URL solta fora d\'un <a>: {url[:50]}')

    for tag in re.findall(r'<(h[1-6])\b', sense_codi(src)):
        if tag not in ('h1', 'h2'):
            errors.append(f'títol <{tag}>: els títols de bloc són <h2>')

    try:
        css = src[src.index('/* === SINAPSI-CSS INICI'):src.index('/* === SINAPSI-CSS FI')]
        css_hash = hashlib.md5(css.encode()).hexdigest()
    except ValueError:
        errors.append('no hi ha el bloc SINAPSI-CSS')
        css_hash = None

    tags = Tags()
    tags.feed(src)
    errors += tags.errors
    if tags.stack:
        errors.append('sense tancar: ' + ', '.join(f'<{t}> (línia {l})' for t, l in tags.stack))

    quiz, ids = quiz_errors(src)
    errors += quiz
    for name, count in collections.Counter(ids).items():
        if count > 1:
            errors.append(f'data-id repetit a la pàgina: {name}')

    if len(re.findall(r'<table', src)) != len(re.findall(r'cq-tablewrap', src)) - 1:
        errors.append('hi ha alguna taula fora de .cq-tablewrap')

    for block in re.findall(r'<pre>(.*?)</pre>', src, re.S):
        for line in html.unescape(re.sub(r'<[^>]+>', '', block)).split('\n'):
            if len(line) > MAX_LINE:
                errors.append(f'línia de codi de {len(line)} caràcters: {line.strip()[:46]}...')

    for kind, body in re.findall(r'<div class="cq-block" data-kind="([^"]*)"[^>]*>(.*?)\n</div>',
                                 src, re.S):
        if kind not in DENSE:
            continue
        words = len(text_of(body).split())
        if words > MAX_WORDS:
            warnings.append(f'bloc «{kind}» amb {words} mots (màxim recomanat {MAX_WORDS})')

    return errors, warnings, css_hash, ids


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    files = pages(only)
    if not files:
        sys.exit(f'No he trobat cap pàgina{" del " + only if only else ""}.')

    hashes, all_ids, bad, warned = collections.defaultdict(list), [], 0, 0
    for path in files:
        errors, warnings, css_hash, ids = check(path)
        hashes[css_hash].append(path.name)
        all_ids += ids
        rel = path.relative_to(ROOT)
        if errors:
            bad += 1
            print(f'\n✗ {rel}')
            for e in errors:
                print(f'    {e}')
        elif warnings:
            warned += 1
            print(f'\n· {rel}')
        for w in warnings:
            print(f'    avís: {w}')

    problems = bad
    if len(hashes) > 1:
        problems += 1
        print('\n✗ el bloc CSS no és igual a totes les pàgines:')
        for h, names in hashes.items():
            print(f'    {str(h)[:8]}  {", ".join(names)}')

    repeated = [i for i, n in collections.Counter(all_ids).items() if n > 1]
    if repeated:
        problems += 1
        print(f'\n✗ data-id repetits entre pàgines: {", ".join(repeated)}')

    print(f'\n{len(files)} pàgines  ·  {len(all_ids)} preguntes  ·  '
          f'{bad} amb errors  ·  {warned} només amb avisos')
    if not problems:
        print('Tot correcte.')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
