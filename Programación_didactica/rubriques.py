#!/usr/bin/env python3
"""Rúbriques de seguiment del mòdul (sense pes: les activitats no es qualifiquen).

    python3 Programación_didactica/rubriques.py            # regenera la pàgina
    python3 Programación_didactica/rubriques.py --check    # comprova la cobertura
    python3 Programación_didactica/rubriques.py --moodle   # text per a Moodle

Dues capes ben separades:

  · La rúbrica OPERATIVA és la que es fa servir per qualificar. Tres dimensions,
    quatre nivells i un descriptor d'una frase. Qualificar un alumne són tres
    clics i desar.

  · La TRAÇABILITAT és el que sosté la nota davant d'una inspecció: quins CA
    entren a cada dimensió, on s'observen i quins CA d'altres RA s'hi reforcen.
    No surt a la rúbrica; viu aquí i a Programación_didactica/cobertura.html.

Els criteris i els continguts surten de curriculum.py, i les activitats on es
treballa cada CA es dedueixen del seu MAP: aquí no es copia res a mà.

Document de programació: publica.py no el copia a docs/.
"""
import importlib.util, pathlib, re, sys, html as _html

CARPETA = pathlib.Path(__file__).resolve().parent
ARREL = CARPETA.parent


def _curriculum():
    spec = importlib.util.spec_from_file_location('curriculum', CARPETA / 'curriculum.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CUR = _curriculum()

NIVELLS = [('10', 'Excel·lent'), ('7,5', 'Assolit'),
           ('5', 'Bàsic'), ('0', 'No assolit')]

# Patró general dels nivells. Cada dimensió l'adapta només quan cal.
PATRO = {
 '10': "Compleix els requisits amb autonomia i corregeix els seus errors.",
 '7,5': "Compleix els requisits essencials i gairebé tots els previstos amb suport puntual.",
 '5': "Aconsegueix el funcionament mínim amb suport freqüent i/o deixa aspectes "
      "secundaris incomplets.",
 '0': "No aconsegueix el funcionament essencial ni amb el suport habitual.",
}

# Una entrada per RA, tres dimensions cadascuna.
#   nom, nivells  → capa operativa: això és tot el que es veu en qualificar.
#   ca, reforc, cont, observa → capa de traçabilitat.
RUBRIQUES = {
 1: [
  {
   'nom': "Comprèn i justifica",
   'nivells': {
    '10': "Explica com funciona l'aplicació web i justifica els requeriments i les decisions amb autonomia.",
    '7,5': "Explica el funcionament i justifica les decisions principals amb suport puntual.",
    '5': "Reconeix les peces bàsiques, però li costa justificar les decisions sense ajuda.",
    '0': "No identifica els elements essencials d'una aplicació web ni amb el suport habitual.",
   },
   'ca': ['1.1', '1.4'],
   'reforc': [],
   'cont': ['1.1', '1.4'],
   'observa': "Com compara estàtic i dinàmic a A1.1, la taula de requeriments "
              "i l'inventari de l'A1.2, i com respon la pregunta final de "
              "cada lliurament.",
  },
  {
   'nom': "Instal·la i personalitza",
   'nivells': {
    '10': "Instal·la i configura el gestor, els usuaris i l'aparença amb autonomia i resol els errors que apareixen.",
    '7,5': "Instal·la i configura els elements essencials amb suport puntual.",
    '5': "Aconsegueix un lloc funcional bàsic amb suport freqüent.",
    '0': "No aconsegueix un lloc funcional ni amb el suport habitual.",
   },
   'ca': ['1.2', '1.3', '1.6', '1.8'],
   'reforc': [],
   'cont': ['1.2', '1.3'],
   'observa': "Els rols, el rol personalitzat i el grup de l'A1.3, la "
              "interfície, els menús i els fils de l'A1.4 i les regles "
              "d'accés del fòrum de l'A1.5.",
  },
  {
   'nom': "Manté, protegeix i verifica",
   'nivells': {
    '10': "Actualitza, protegeix, copia i prova el lloc pel seu compte i corregeix les incidències.",
    '7,5': "Actualitza, copia i prova el lloc i resol les incidències habituals amb suport puntual.",
    '5': "Fa les tasques de manteniment quan se li recorden i resol els errors coneguts amb suport freqüent.",
    '0': "No sap mantenir ni comprovar el lloc ni amb el suport habitual.",
   },
   'ca': ['1.5', '1.7', '1.9', '1.10'],
   'reforc': [],
   'cont': ['1.5'],
   'observa': "A l'A1.6, la taula d'actualitzacions, els mecanismes de "
              "seguretat, la còpia que sap restaurar i les tres passades de "
              "la llista de proves.",
  },
 ],
 2: [
  {
   'nom': "Comprèn i justifica",
   'nivells': {
    '10': "Explica l'estructura del campus i la jerarquia de directoris generada i justifica les decisions d'administració amb autonomia.",
    '7,5': "Explica l'estructura del lloc i justifica les decisions principals amb suport puntual.",
    '5': "Reconeix les parts del campus, però li costa dir on va cada cosa sense ajuda.",
    '0': "No distingeix el codi, les dades i la base de dades ni amb el suport habitual.",
   },
   'ca': ['2.1'],
   'reforc': [],
   'cont': ['2.1'],
   'observa': "Com explica a l'A2.1 on acaba un fitxer pujat, i com respon "
              "la pregunta final de cada lliurament.",
  },
  {
   'nom': "Administra el campus",
   'nivells': {
    '10': "Configura el lloc, els usuaris, els cursos i les activitats de comunicació amb autonomia i resol els errors que apareixen.",
    '7,5': "Configura els elements essencials del campus amb suport puntual.",
    '5': "Aconsegueix un campus funcional bàsic amb suport freqüent.",
    '0': "No aconsegueix un campus utilitzable ni amb el suport habitual.",
   },
   'ca': ['2.2', '2.3', '2.4'],
   'reforc': [],
   'cont': ['2.2', '2.3'],
   'observa': "L'aspecte i les normatives de l'A2.1, i els cursos, la càrrega "
              "d'usuaris, els grups i el fòrum de l'A2.2.",
  },
  {
   'nom': "Manté, protegeix i verifica",
   'nivells': {
    '10': "Copia, restaura, mou cursos, llegeix els informes i tanca el lloc pel seu compte i corregeix les incidències.",
    '7,5': "Fa les còpies, les restauracions i les comprovacions amb suport puntual.",
    '5': "Fa les tasques de manteniment quan se li recorden i amb suport freqüent.",
    '0': "No sap copiar, restaurar ni comprovar el campus ni amb el suport habitual.",
   },
   'ca': ['2.5', '2.6', '2.7', '2.8'],
   'reforc': [],
   'cont': [],
   'observa': "A l'A2.3, el curs que mou amb un .mbz, la còpia que sap "
              "restaurar, els informes que interpreta i com justifica el "
              "bloqueig d'IP.",
  },
 ],
 3: [
  {
   'nom': "Comprèn i justifica",
   'nivells': {
    '10': "Explica la utilitat d'un servei de gestió d'arxius web, compara aplicacions i justifica la triada amb autonomia.",
    '7,5': "Explica la utilitat del servei i compara aplicacions amb suport puntual.",
    '5': "Reconeix per a què serveix, però li costa comparar-lo amb altres solucions.",
    '0': "No distingeix un gestor d'arxius web d'una carpeta compartida ni amb el suport habitual.",
   },
   'ca': ['3.1', '3.2'],
   'reforc': [],
   'cont': ['3.1'],
   'observa': "La taula comparativa de l'A3.1 i com respon la pregunta final "
              "de cada lliurament.",
  },
  {
   'nom': "Instal·la i comparteix",
   'nivells': {
    '10': "Instal·la i adapta el gestor, crea comptes i grups i munta els recursos compartits amb autonomia.",
    '7,5': "Instal·la el gestor i configura comptes i comparticions amb suport puntual.",
    '5': "Arriba a un servei funcional bàsic amb suport freqüent.",
    '0': "No aconsegueix un servei utilitzable ni amb el suport habitual.",
   },
   'ca': ['3.3', '3.4', '3.5'],
   'reforc': [],
   'cont': ['3.1', '3.2', '3.3'],
   'observa': "La instal·lació amb les dades fora del web de l'A3.1 i la "
              "matriu de permisos de l'A3.2.",
  },
  {
   'nom': "Ordena, troba i protegeix",
   'nivells': {
    '10': "Aplica criteris d'indexació i informació addicional i comprova la seguretat del gestor pel seu compte.",
    '7,5': "Etiqueta, documenta i fa les comprovacions de seguretat amb suport puntual.",
    '5': "Ordena i comprova quan se li recorda i amb suport freqüent.",
    '0': "No aplica cap criteri d'ordre ni comprova la seguretat ni amb el suport habitual.",
   },
   'ca': ['3.6', '3.7', '3.8'],
   'reforc': [],
   'cont': [],
   'observa': "Els criteris d'indexació, les etiquetes i l'informe de "
              "seguretat de l'A3.3.",
  },
 ],
 4: [
  {
   'nom': "Comprèn i tria",
   'nivells': {
    '10': "Explica la utilitat de l'ofimàtica web, descriu les aplicacions i justifica la suite triada amb autonomia.",
    '7,5': "Descriu les aplicacions i justifica la tria amb suport puntual.",
    '5': "Reconeix per a què serveix cada aplicació, però li costa justificar la tria.",
    '0': "No distingeix l'ofimàtica web de la d'escriptori ni amb el suport habitual.",
   },
   'ca': ['4.1', '4.2'],
   'reforc': [],
   'cont': ['4.1'],
   'observa': "La taula comparativa i la recomanació de l'A4.1, i com respon "
              "la pregunta final de cada lliurament.",
  },
  {
   'nom': "Desplega i treballa en equip",
   'nivells': {
    '10': "Desplega l'entorn, domina les prestacions de cada aplicació i treballa de manera col·laborativa amb autonomia.",
    '7,5': "Fa servir les aplicacions i treballa amb els companys amb suport puntual.",
    '5': "Aconsegueix el resultat bàsic amb suport freqüent i poca col·laboració real.",
    '0': "No arriba a fer servir les aplicacions de manera col·laborativa ni amb el suport habitual.",
   },
   'ca': ['4.3', '4.6', '4.7'],
   'reforc': [],
   'cont': ['4.1'],
   'observa': "L'entorn i el complement de l'A4.1, i els suggeriments, els "
              "comentaris i l'historial de l'A4.2.",
  },
  {
   'nom': "Gestiona accessos i protegeix",
   'nivells': {
    '10': "Gestiona comptes i permisos i aplica criteris de seguretat i de protecció de dades pel seu compte.",
    '7,5': "Gestiona els permisos i aplica les mesures de seguretat amb suport puntual.",
    '5': "Comparteix i protegeix quan se li recorda i amb suport freqüent.",
    '0': "No controla qui accedeix als documents ni amb el suport habitual.",
   },
   'ca': ['4.4', '4.5'],
   'reforc': [],
   'cont': ['4.2', '4.3'],
   'observa': "La taula d'accessos, la matriu de proves i l'auditoria de "
              "comparticions de l'A4.3.",
  },
 ],
 5: [
  {
   'nom': "Comprèn i descriu",
   'nivells': {
    '10': "Descriu les aplicacions web d'escriptori i explica el camí d'un correu i el funcionament d'una agenda amb autonomia.",
    '7,5': "Descriu les aplicacions i explica el funcionament amb suport puntual.",
    '5': "Reconeix les peces, però li costa explicar com encaixen sense ajuda.",
    '0': "No distingeix el client del servidor ni amb el suport habitual.",
   },
   'ca': ['5.1'],
   'reforc': [],
   'cont': ['5.1'],
   'observa': "Com explica a l'A5.1 per què encara no pot llegir el correu al "
              "navegador, i les capçaleres que sap interpretar.",
  },
  {
   'nom': "Instal·la i integra",
   'nivells': {
    '10': "Instal·la el servidor, el correu web i el calendari i els integra i verifica pel seu compte.",
    '7,5': "Instal·la i integra les aplicacions amb suport puntual.",
    '5': "Arriba a un servei funcional bàsic amb suport freqüent.",
    '0': "No aconsegueix un correu web utilitzable ni amb el suport habitual.",
   },
   'ca': ['5.2', '5.3', '5.5', '5.6'],
   'reforc': [],
   'cont': ['5.1'],
   'observa': "La integració del client amb el servidor a l'A5.2 i les proves "
              "entre dos comptes; el calendari sincronitzat de l'A5.3.",
  },
  {
   'nom': "Gestiona i aprofita",
   'nivells': {
    '10': "Gestiona els comptes i treu partit de les prestacions de cada aplicació amb autonomia.",
    '7,5': "Gestiona els comptes i fa servir les prestacions principals amb suport puntual.",
    '5': "Crea comptes i esdeveniments quan se li indica, amb suport freqüent.",
    '0': "No sap donar d'alta ni de baixa un compte ni amb el suport habitual.",
   },
   'ca': ['5.4', '5.7'],
   'reforc': [],
   'cont': ['5.2'],
   'observa': "Les altes, els àlies i la baixa de l'A5.1, i els convidats, les "
              "repeticions i les tasques de l'A5.3.",
  },
 ],
}

PENDENT = ("Si no hi ha hagut prou ocasió d'observar una dimensió, no s'hi posa "
           "un 0: queda <strong>pendent de verificació</strong> fins que l'alumne "
           "en faci una demostració pràctica breu o una verificació equivalent.")

COMENTARIS = ("Els comentaris són opcionals. Només s'escriuen davant d'una "
              "incidència, una situació excepcional o informació que valgui la "
              "pena deixar registrada.")

CSS_EXTRA = '''
  .rub { max-width: 1080px; }
  .rub-avis {
    max-width: 1080px; margin: 0 auto 20px; padding: 12px 18px;
    background: var(--warn-soft); border: 1px solid var(--warn-line);
    border-radius: 8px; font-size: .88rem; color: var(--warn); }
  .rub-avis strong { font-weight: 600; }
  .rub-meta { font-size: .88rem; color: var(--muted); margin: 0 0 14px; }
  .rub-table { border-collapse: collapse; width: 100%; table-layout: fixed;
               font-size: .88rem; line-height: 1.45; }
  .rub-table th, .rub-table td {
    border: 1px solid var(--rule); padding: 10px 12px; text-align: left;
    vertical-align: top; }
  .rub-table thead th {
    background: var(--accent-soft); border-color: var(--accent-line);
    font-family: var(--font-display); color: var(--accent); }
  .rub-table thead th .pts {
    display: block; font-family: var(--font-mono); font-size: 1.05rem;
    font-weight: 700; line-height: 1.2; }
  .rub-table thead th .lvl { font-size: .78rem; font-weight: 500; }
  .rub-table thead th:first-child { background: var(--card); color: var(--muted);
                                    border-color: var(--rule); }
  .rub-table col.c0 { width: 17%; }
  .rub-table col.c1, .rub-table col.c2, .rub-table col.c3, .rub-table col.c4 {
    width: 20.75%; }
  .rub-table td.dim { background: var(--paper); font-family: var(--font-display);
                      font-weight: 700; color: var(--ink); }
  .rub-table td.n10 { background: var(--ok-soft); }
  .rub-table td.n0  { background: var(--ko-soft); }
  .rub-legend { list-style: none; margin: 4px 0 0; padding: 0; }
  .rub-legend li { display: grid; grid-template-columns: 110px 1fr; gap: 12px;
                   margin-bottom: 8px; }
  .rub-legend .p { font-family: var(--font-mono); font-weight: 700;
                   color: var(--accent); }
  .rub-trac { font-size: .85rem; }
  .rub-trac .dimcol { font-family: var(--font-display); font-weight: 600; }
  .rub-trac .fora { color: var(--warn); }
  @media print {
    .rub { max-width: none; border: none; padding: 0; }
    .rub-avis { display: none; }
  }
'''


pagines_de = CUR.pagines_de     # on es treballa un criteri o un contingut
instrument = CUR.instrument     # amb què s'avalua realment


def comprova():
    """Cada CA del RA a una dimensió i una sola, i cap codi inventat."""
    err = []
    for ra, dims in RUBRIQUES.items():
        propis, vistos = [c for c in CUR.CA if c.startswith(f'{ra}.')], []
        for d in dims:
            for c in d['ca'] + d['reforc']:
                if c not in CUR.CA:
                    err.append(f"RA{ra} · {d['nom']}: el criteri {c} no és al currículum.")
            for c in d['cont']:
                if c not in CUR.CONT:
                    err.append(f"RA{ra} · {d['nom']}: el contingut {c} no és al currículum.")
            for c in d['ca']:
                if not c.startswith(f'{ra}.'):
                    err.append(f"RA{ra} · {d['nom']}: {c} no és del RA{ra}; va a «reforç».")
            vistos += d['ca']
            if set(d['nivells']) != {p for p, _ in NIVELLS}:
                err.append(f"RA{ra} · {d['nom']}: falta el descriptor d'algun nivell.")
            for punts, text in d['nivells'].items():
                if text.count('.') > 1:
                    err.append(f"RA{ra} · {d['nom']} · nivell {punts}: el descriptor "
                               f"ha de ser una sola frase.")
        if faltants := [c for c in propis if c not in vistos]:
            err.append(f'RA{ra}: criteris fora de la rúbrica: ' + ', '.join(faltants))
        if repetits := sorted({c for c in vistos if vistos.count(c) > 1}):
            err.append(f'RA{ra}: criteris a més d\'una dimensió: ' + ', '.join(repetits))
        if len(dims) != 3:
            err.append(f'RA{ra}: la rúbrica té {len(dims)} dimensions i n\'ha de tenir 3.')
    for e in err:
        print('ERROR:', e)
    if not err:
        fet = ', '.join(f'RA{ra}' for ra in sorted(RUBRIQUES))
        print(f'D\'acord: {len(RUBRIQUES)} rúbriques ({fet}), '
              f'{sum(len(d) for d in RUBRIQUES.values())} dimensions, '
              f'descriptors d\'una frase.')
    return 1 if err else 0


def moodle():
    """El text exacte de la rúbrica, per enganxar-lo al formulari de Moodle."""
    for ra in sorted(RUBRIQUES):
        print(f'\n=== RA{ra} · {CUR.RA_NOM[str(ra)]} '
              f'— rúbrica de seguiment (sense pes) ===')
        for d in RUBRIQUES[ra]:
            print(f'\n{d["nom"]}')
            for punts, nom in NIVELLS:
                print(f'  [{punts}] {nom}: {d["nivells"][punts]}')


def e(t):
    return _html.escape(t)


def taula_operativa(dims):
    out = ['<div class="cq-tablewrap"><table class="rub-table">',
           '<colgroup><col class="c0"><col class="c1"><col class="c2">'
           '<col class="c3"><col class="c4"></colgroup>',
           '<thead><tr><th>Dimensió</th>']
    for punts, nom in NIVELLS:
        out.append(f'<th><span class="pts">{punts}</span>'
                   f'<span class="lvl">{nom}</span></th>')
    out.append('</tr></thead><tbody>')
    for d in dims:
        out.append(f'<tr><td class="dim">{e(d["nom"])}</td>')
        for punts, _ in NIVELLS:
            cls = ' class="n10"' if punts == '10' else \
                  ' class="n0"' if punts == '0' else ''
            out.append(f'<td{cls}>{e(d["nivells"][punts])}</td>')
        out.append('</tr>')
    out += ['</tbody></table></div>']
    return '\n'.join(out)


def taula_tracabilitat(ra, dims):
    """Un CA per fila: enunciat, dimensió que el recull, on es treballa i prova."""
    files = []
    for d in dims:
        for c in d['ca'] + d['reforc']:
            marca = '' if c in d['ca'] else \
                    f' <span class="fora">(reforç · qualifica al RA{c.split(".")[0]})</span>'
            on = ' · '.join(pagines_de(c)) or '<strong>sense cobrir</strong>'
            inst = instrument(c)
            inst = inst if inst.startswith('Pràctica') else f'<em>{inst}</em>'
            files.append(f'    <tr><td><code>{c}</code>{marca}</td>'
                         f'<td>{e(CUR.CA[c])}</td>'
                         f'<td class="dimcol">{e(d["nom"])}</td>'
                         f'<td>{on}</td><td>{inst}</td></tr>')
    conts = []
    for c in sorted({c for d in dims for c in d['cont']}):
        on = ' · '.join(pagines_de(c, contingut=True)) or '<strong>sense cobrir</strong>'
        quines = ', '.join(d['nom'] for d in dims if c in d['cont'])
        conts.append(f'    <tr><td><code>C {c}</code></td>'
                     f'<td>{e(CUR.CONT[c])}</td>'
                     f'<td class="dimcol">{e(quines)}</td>'
                     f'<td>{on}</td><td>—</td></tr>')
    obs = '\n'.join(f'  <p><span class="lbl">{e(d["nom"])}</span> {e(d["observa"])}</p>'
                    for d in dims)
    return ('<div class="cq-block rub" data-kind="traçabilitat">\n'
            f'  <h2>D\'on surt la nota del RA{ra}</h2>\n'
            '  <p class="rub-meta">Cada criteri i cada contingut del RA, la '
            'dimensió de la rúbrica que el recull, les pàgines que el treballen '
            'i l\'instrument que l\'avalua. Les dues últimes columnes surten del '
            '<code>MAP</code> i del <code>PROVA</code> de '
            '<code>curriculum.py</code>: no s\'escriuen a mà. Els continguts '
            's\'ancoren a la teoria, que és on s\'expliquen. </p>\n'
            '  <div class="cq-tablewrap"><table class="cq-table rub-trac">\n'
            '    <thead><tr><th>Criteri</th><th>Enunciat</th><th>Dimensió</th>'
            '<th>On es treballa</th><th>Instrument</th></tr></thead><tbody>\n' +
            '\n'.join(files + conts) +
            '\n    </tbody></table></div>\n'
            '  <h2>Què s\'observa a l\'aula</h2>\n'
            '  <p class="rub-meta">La taula diu quins criteris es treballen. '
            'Això diu quina conducta mira el professor per decidir el nivell.</p>\n'
            + obs + '\n</div>')


def pagina():
    css = re.search(r'/\* === SINAPSI-CSS INICI.*?/\* === SINAPSI-CSS FI[^\n]*\n',
                    (ARREL / 'index.html').read_text(encoding='utf8'), re.S).group(0)

    out = ['<!DOCTYPE html>', '<html lang="ca">', '<head>',
           '<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           '<title>Rúbriques de seguiment — 0228 Aplicacions web</title>',
           '<style>', css, CSS_EXTRA, '</style>', '</head>', '<body>',
           '<header class="cq-header">',
           '  <div class="eyebrow">CFGM SMX · Mòdul 0228 · ús intern</div>',
           '  <h1>Rúbriques de seguiment</h1>',
           '  <p class="lede">Una rúbrica per resultat d\'aprenentatge i alumne. '
           'No té pes a la nota: serveix per al seguiment de les activitats '
           'i per a la retroacció a l\'alumnat. La nota del RA són la '
           'pràctica principal (60 %), amb la rúbrica de la seva pàgina, i '
           'l\'examen tipus test a Moodle (40 %).</p>',
           '</header>',
           '\n<div class="rub-avis"><strong>Document de programació.</strong> '
           'La rúbrica es qualifica a Moodle, no en aquesta pàgina: aquí hi ha '
           'el text que s\'hi carrega i la traçabilitat que el sosté. No es '
           'publica al web de l\'alumnat.</div>',
           '\n<div class="cq-block rub" data-kind="com s\'usa">',
           '  <h2>Com es fa servir</h2>',
           '  <p>La rúbrica s\'actualitza mentre dura el RA i es tanca quan '
           's\'acaba. Qualificar un alumne és triar un nivell a cada dimensió i '
           'desar. Cada dimensió val un terç i el nivell es decideix amb dos '
           'criteris alhora: <strong>què aconsegueix</strong> l\'alumne i '
           '<strong>amb quant suport</strong>.</p>',
           '  <ul class="rub-legend">']
    for punts, nom in NIVELLS:
        out.append(f'    <li><span class="p">{punts} · {nom}</span>'
                   f'<span>{e(PATRO[punts])}</span></li>')
    out += ['  </ul>',
            f'  <p>{PENDENT}</p>',
            f'  <p>{e(COMENTARIS)}</p>',
            '</div>']

    for ra in sorted(RUBRIQUES):
        dims = RUBRIQUES[ra]
        out += [f'\n<div class="cq-block rub" data-kind="RA{ra} · rúbrica">',
                f'  <h2>RA{ra} · {CUR.RA_NOM[str(ra)]}</h2>',
                '  <p class="rub-meta">Això, i res més, és el que es veu en '
                'qualificar.</p>',
                taula_operativa(dims),
                '</div>',
                taula_tracabilitat(ra, dims)]

    out += ['</body>', '</html>']
    sortida = CARPETA / 'rubriques.html'
    sortida.write_text('\n'.join(out) + '\n', encoding='utf8')
    print(f'{sortida.relative_to(ARREL)}  ·  {len(RUBRIQUES)} de 5 rúbriques escrites')


if __name__ == '__main__':
    if comprova():
        sys.exit('La rúbrica no passa les comprovacions; no s\'escriu res.')
    if '--moodle' in sys.argv:
        moodle()
    elif '--check' not in sys.argv:
        pagina()
