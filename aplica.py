#!/usr/bin/env python3
"""Torna a aplicar a totes les pàgines allò que no s'escriu a mà.

    python3 aplica.py          # tot el mòdul
    python3 aplica.py RA2      # només un RA

Tres feines, totes derivades d'una única font i totes idempotents: passar-lo
dues vegades seguides deixa els fitxers igual.

  1. L'estil. El bloc entre els marcadors SINAPSI-CSS surt de
     _identitat/sinapsi.css i s'escriu igual a totes les pàgines.
  2. La navegació. La barra de dalt i el pas a la pàgina següent surten del
     RAn/index.html, que ja diu en quin ordre van les pàgines. Van entre els
     marcadors NAVEGACIÓ i no es toquen a mà.
  3. Els enllaços creuats. Cada «T2.4», «G4.1», «A3.2» o «P1.1» que apareix dins d'un
     bloc es converteix en un enllaç a la pàgina que toca.

Res d'això entra dins dels blocs de contingut, així que l'editor no s'hi
barreja: escriu els blocs i la capçalera, i aquest script, la resta.
"""
import os
import pathlib
import re
import sys

import importlib

fesweb = importlib.import_module('fes-web')

ROOT = pathlib.Path(__file__).resolve().parent
CSS = ROOT / '_identitat' / 'sinapsi.css'

CSS_INICI = '/* === SINAPSI-CSS INICI'
CSS_FI = '/* === SINAPSI-CSS FI'

NAV_INICI = '<!-- === NAVEGACIÓ INICI === -->'
NAV_FI = '<!-- === NAVEGACIÓ FI === -->'
PAG_INICI = '<!-- === PEU DE NAVEGACIÓ INICI === -->'
PAG_FI = '<!-- === PEU DE NAVEGACIÓ FI === -->'

REF = r'[TGAP](?:\d+|X)\.\d+|RA(?:\d+|X)'
REF_RE = re.compile(r'\b(' + REF + r')\b')
# Trossos on no s'hi toca: codi, enllaços que ja existeixen i el motor del test.
PROTEGIT_RE = re.compile(r'<pre\b.*?</pre>|<a\b.*?</a>|<code\b.*?</code>', re.S)
BLOC_RE = re.compile(r'(<div class="cq-block"[^>]*>)(.*?)(\n</div>)', re.S)


# ---------------------------------------------------------------- estil

def aplica_estil(src):
    """Reemplaça el bloc SINAPSI-CSS sencer, marcadors inclosos."""
    nou = CSS.read_text(encoding='utf-8')
    nou = nou[nou.index(CSS_INICI):].rstrip('\n')
    fi = src.index('\n', src.index(CSS_FI)) + 1
    return src[:src.index(CSS_INICI)] + nou + '\n' + src[fi:]


def aplica_principal(src):
    """Delimita el contingut de lectura amb un landmark HTML principal."""
    if '<main>' in src:
        return src
    src = src.replace('<header class="cq-header">',
                      '<main>\n<header class="cq-header">', 1)
    close_at = src.find('<script')
    if close_at < 0:
        close_at = src.index('</body>')
    return src[:close_at] + '</main>\n' + src[close_at:]


# ------------------------------------------------------------ navegació

def entre(src, inici, fi, contingut):
    """Escriu `contingut` entre els dos marcadors, creant-los si no hi són.
    Retorna (src, on_inserir) — la inserció la decideix qui crida."""
    if inici in src and fi in src:
        a = src.index(inici)
        b = src.index(fi) + len(fi)
        return src[:a] + contingut + src[b:]
    return None


def barra(enllac, text, posicio):
    return (f'{NAV_INICI}\n<nav class="cq-nav">\n  <div class="inner">\n'
            f'    <a href="{enllac}">‹ {text}</a>\n'
            f'    <span class="pos">{posicio}</span>\n'
            f'  </div>\n</nav>\n{NAV_FI}')


def targeta(classe, direccio, ref, titol, enllac):
    etiqueta = f'{direccio} · {ref}' if ref else direccio
    return (f'  <a class="{classe}" href="{enllac}">\n'
            f'    <span class="dir">{etiqueta}</span>\n'
            f'    <span class="ttl">{titol}</span></a>')


def pager(anterior, seguent):
    return (f'{PAG_INICI}\n<nav class="cq-pager">\n'
            f'{anterior}\n{seguent}\n</nav>\n{PAG_FI}')


def escriu_navegacio(src, barra_html, pager_html):
    """Posa la barra just després de <body> i el pas següent just abans del
    <script>. Cap de les dues toca mai els blocs ni la capçalera."""
    nou = entre(src, NAV_INICI, NAV_FI, barra_html)
    src = nou if nou is not None else src.replace(
        '<body>\n', '<body>\n' + barra_html + '\n\n', 1)

    nou = entre(src, PAG_INICI, PAG_FI, pager_html)
    if nou is not None:
        return nou
    i = src.index('\n<script>')
    return src[:i] + '\n' + pager_html + '\n' + src[i:]


# ------------------------------------------------------- enllaços creuats

def enllaça(src, mapa, propi, origen):
    """Converteix les referències a altres pàgines en enllaços, només dins
    dels blocs de contingut i fora del codi i dels enllaços que ja hi són."""

    def per_bloc(bloc):
        cos = bloc.group(2)

        def marca(text):
            def sub(m):
                ref = m.group(1)
                desti = mapa.get(ref)
                if not desti or ref == propi:
                    return m.group(0)
                rel = os.path.relpath(ROOT / desti, origen)
                return f'<a class="cq-ref" href="{rel}">{ref}</a>'
            return REF_RE.sub(sub, text)

        # El <strong>G4.1</strong> es reemplaça sencer: l'enllaç ja destaca.
        cos = re.sub(r'<strong>(' + REF + r')</strong>',
                     lambda m: marca(m.group(1)), cos)

        trossos, i = [], 0
        for p in PROTEGIT_RE.finditer(cos):
            trossos.append(marca(cos[i:p.start()]))
            trossos.append(p.group(0))
            i = p.end()
        trossos.append(marca(cos[i:]))
        return bloc.group(1) + ''.join(trossos) + bloc.group(3)

    return BLOC_RE.sub(per_bloc, src)


# ------------------------------------------------------------------ mòdul

def recull():
    """(mapa de referències, i per a cada RA la seva llista de pàgines)."""
    mapa, per_ra = {}, {}
    for ra in fesweb.ra_folders():
        h1, lede, pagines = fesweb.index_pages(ra)
        per_ra[ra.name] = (lede, pagines)
        mapa[ra.name] = f'{ra.name}/index.html'
        for _, ref, _, _, _, cami in pagines:
            mapa[ref] = cami
    return mapa, per_ra


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    mapa, per_ra = recull()
    noms = [n for n in per_ra if not only or n == only]
    if not noms:
        sys.exit(f'No he trobat cap RA{" anomenat " + only if only else ""}.')

    tocats = 0
    for nom in noms:
        lede, pagines = per_ra[nom]
        total = len(pagines)
        for i, (_, ref, titol, _, _, cami) in enumerate(pagines):
            path = ROOT / cami
            src = original = path.read_text(encoding='utf-8')
            src = aplica_estil(src)
            src = aplica_principal(src)

            if i:
                _, pref, ptit, _, _, pcami = pagines[i - 1]
                ant = targeta('prev', 'Anterior', pref, ptit,
                              os.path.relpath(ROOT / pcami, path.parent))
            else:
                ant = targeta('prev', 'Torna a', nom, lede,
                              os.path.relpath(ROOT / nom / 'index.html', path.parent))
            if i + 1 < total:
                _, sref, stit, _, _, scami = pagines[i + 1]
                seg = targeta('next', 'Següent', sref, stit,
                              os.path.relpath(ROOT / scami, path.parent))
            else:
                seg = targeta('next', 'Has acabat el', nom, lede,
                              os.path.relpath(ROOT / nom / 'index.html', path.parent))

            src = escriu_navegacio(
                src,
                barra(os.path.relpath(ROOT / nom / 'index.html', path.parent),
                      lede, f'{ref} · {i + 1}/{total}'),
                pager(ant, seg))
            src = enllaça(src, mapa, ref, path.parent)

            if src != original:
                path.write_text(src, encoding='utf-8')
                tocats += 1

        # L'índex del RA: només estil i barra cap al portal del mòdul.
        path = ROOT / nom / 'index.html'
        src = original = path.read_text(encoding='utf-8')
        src = aplica_estil(src)
        src = aplica_principal(src)
        ras = sorted(per_ra)
        j = ras.index(nom)
        ant = (targeta('prev', 'Anterior', ras[j - 1], per_ra[ras[j - 1]][0],
                       f'../{ras[j - 1]}/index.html') if j else
               targeta('prev', 'Torna al', '', 'Índex del mòdul', '../index.html'))
        seg = (targeta('next', 'Següent', ras[j + 1], per_ra[ras[j + 1]][0],
                       f'../{ras[j + 1]}/index.html') if j + 1 < len(ras) else
               targeta('next', 'Torna a l\'', '', 'Índex del mòdul', '../index.html'))
        src = escriu_navegacio(
            src, barra('../index.html', 'Aplicacions Web (0228)',
                       f'{nom} · {j + 1}/{len(ras)}'),
            pager(ant, seg))
        src = enllaça(src, mapa, nom, path.parent)
        if src != original:
            path.write_text(src, encoding='utf-8')
            tocats += 1

    # El portal del mòdul: només l'estil.
    if not only:
        path = ROOT / 'index.html'
        src = original = path.read_text(encoding='utf-8')
        src = aplica_estil(src)
        src = aplica_principal(src)
        if src != original:
            path.write_text(src, encoding='utf-8')
            tocats += 1

    print(f'{tocats} pàgines actualitzades.')


if __name__ == '__main__':
    main()
