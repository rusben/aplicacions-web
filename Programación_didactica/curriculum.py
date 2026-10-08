#!/usr/bin/env python3
"""Traçabilitat amb el currículum de la Generalitat (0228 Aplicacions web).

    python3 Programación_didactica/curriculum.py            # blocs curriculars
    python3 Programación_didactica/curriculum.py --matriu   # i matriu

El mapa MAP d'aquest fitxer és l'única font: els blocs de les pàgines i la
matriu de cobertura en surten tots dos. La matriu és per al professorat i es
queda al repositori privat, dins de Programación_didactica/: publica.py no la copia a docs/.
"""
import re, sys, pathlib, html as _html

ARREL = pathlib.Path(__file__).resolve().parent.parent

CA = {
 '1.1': "Identifica els requeriments necessaris per instal·lar gestors de continguts.",
 '1.2': "Gestiona usuaris amb rols diferents.",
 '1.3': "Personalitza la interfície del gestor de continguts.",
 '1.4': "Realitza proves de funcionament.",
 '1.5': "Realitza tasques d'actualització del gestor de continguts, especialment les de seguretat.",
 '1.6': "Instal·la i configura els mòduls i menús necessaris.",
 '1.7': "Activa i configura els mecanismes de seguretat proporcionats pel propi gestor de continguts.",
 '1.8': "Habilita fòrums i estableix regles d'accés.",
 '1.9': "Realitza proves de funcionament.",
 '1.10': "Realitza còpies de seguretat dels continguts del gestor.",
 '2.1': "Reconeix l'estructura del lloc i la jerarquia de directoris generada.",
 '2.2': "Realitza modificacions en l'estètica o aspecte del lloc.",
 '2.3': "Manipula i genera perfils personalitzats.",
 '2.4': "Comprova la funcionalitat de les comunicacions mitjançant fòrums, consultes, entre d'altres.",
 '2.5': "Importa i exporta continguts en diferents formats.",
 '2.6': "Realitza còpies de seguretat i restauracions.",
 '2.7': "Realitza informes d'accés i utilització del lloc.",
 '2.8': "Comprova la seguretat del lloc.",
 '3.1': "Estableix la utilitat d'un servei de gestió d'arxius web.",
 '3.2': "Descriu diferents aplicacions de gestió d'arxius web.",
 '3.3': "Instal·la i adapta una eina de gestió d'arxius web.",
 '3.4': "Crea i classifica comptes d'usuari en funció dels seus permisos.",
 '3.5': "Gestiona arxius i directoris.",
 '3.6': "Utilitza arxius d'informació addicional.",
 '3.7': "Aplica criteris d'indexació sobre els arxius i directoris.",
 '3.8': "Comprova la seguretat del gestor d'arxius.",
 '4.1': "Estableix la utilitat de les aplicacions d'ofimàtica web.",
 '4.2': "Descriu diferents aplicacions d'ofimàtica web (processador de textos, full de càlcul, entre altres).",
 '4.3': "Instal·la aplicacions d'ofimàtica web.",
 '4.4': "Gestiona els comptes d'usuari.",
 '4.5': "Aplica criteris de seguretat en l'accés dels usuaris.",
 '4.6': "Reconeix les prestacions específiques de cadascuna de les aplicacions instal·lades.",
 '4.7': "Utilitza les aplicacions de forma col·laborativa.",
 '5.1': "Descriu diferents aplicacions web d'escriptori.",
 '5.2': "Instal·la aplicacions per a proveir d'accés web al servei de correu electrònic.",
 '5.3': "Configura les aplicacions per a integrar-les amb un servidor de correu.",
 '5.4': "Gestiona els comptes d'usuari.",
 '5.5': "Verifica l'accés al correu electrònic.",
 '5.6': "Instal·la aplicacions de calendari web.",
 '5.7': "Reconeix les prestacions específiques de les aplicacions instal·lades (cites, tasques, entre altres).",
}

CONT = {
 '1.1': "Instal·lació en sistemes operatius lliures i propietaris.",
 '1.2': "Creació d'usuaris i grups d'usuaris.",
 '1.3': "Utilització de la interfície gràfica. Personalització de l'entorn. Funcionalitats proporcionades pel gestor de continguts. Sindicació.",
 '1.4': "Funcionament dels gestors de continguts.",
 '1.5': "Actualitzacions del gestor de continguts. Configuració de mòduls i menús.",
 '2.1': "Elements lògics: comunicació, materials i activitats.",
 '2.2': "Instal·lació en sistemes operatius lliures i propietaris. Modes de registre. Interfície gràfica associada. Personalització de l'entorn. Navegació i edició.",
 '2.3': "Creació de cursos seguint especificacions. Gestió d'usuaris i grups. Activació de funcionalitats.",
 '3.1': "Instal·lació. Navegació i operacions bàsiques. Administració del gestor.",
 '3.2': "Usuaris i permisos. Tipus d'usuari.",
 '3.3': "Creació de recursos compartits.",
 '4.1': "Instal·lació. Utilització de les aplicacions instal·lades.",
 '4.2': "Gestió d'usuaris i permisos associats.",
 '4.3': "Comprovació de la seguretat.",
 '5.1': "Aplicacions de correu web. Instal·lació.",
 '5.2': "Gestió d'usuaris.",
}

RA = {
 '1': "Instal·la gestors de continguts, identificant-ne les aplicacions i configurant-los segons requeriments.",
 '2': "Instal·la sistemes de gestió d'aprenentatge a distància, descrivint-ne l'estructura del lloc i la jerarquia de directoris generada.",
 '3': "Instal·la serveis de gestió d'arxius web, identificant-ne les aplicacions i verificant-ne la integritat.",
 '4': "Instal·la aplicacions d'ofimàtica web, descrivint-ne les característiques i entorns d'ús.",
 '5': "Instal·la aplicacions web d'escriptori, descrivint-ne les característiques i entorns d'ús.",
}

# De cada pàgina: (continguts, criteris). Les guies també hi són: surten a la
# matriu i al quadre del RA, però no porten bloc a la pàgina. Els criteris de
# les pràctiques no s'escriuen aquí: surten de la seva rúbrica (PRACTIQUES).
MAP = {
 'RA1/teoria/t1-1-com-funciona-una-aplicacio-web': (['1.1', '1.4'], ['1.1']),
 'RA1/teoria/t1-2-html-i-css':                     (['1.3'], ['1.3']),
 'RA1/teoria/t1-3-gestors-de-continguts':          (['1.1', '1.3', '1.4', '1.5'], ['1.1', '1.3', '1.6']),
 'RA1/teoria/t1-4-usuaris-i-rols':                 (['1.2'], ['1.2', '1.8']),
 'RA1/teoria/t1-5-mantenir-un-gestor':             (['1.5'], ['1.4', '1.5', '1.7', '1.9', '1.10']),
 'RA1/guies/g1-1-entorn-de-laboratori':            (['1.1'], ['1.1']),
 'RA1/guies/g1-2-pila-lamp':                       (['1.1'], ['1.1', '1.4']),
 'RA1/guies/g1-3-wordpress':                       (['1.1', '1.2', '1.3', '1.5'], ['1.2', '1.3', '1.5', '1.6', '1.7', '1.8', '1.9', '1.10']),
 'RA1/guies/g1-4-migrar-wordpress':                (['1.1'], ['1.4', '1.9', '1.10']),
 'RA1/activitats/a1-1-estatic-i-dinamic':          (['1.1', '1.4'], ['1.1', '1.4']),
 'RA1/activitats/a1-2-requeriments-i-instal-lacio': (['1.1', '1.4'], ['1.1', '1.4']),
 'RA1/activitats/a1-3-usuaris-grups-i-rols':       (['1.2'], ['1.2']),
 'RA1/activitats/a1-4-interficie-menus-i-sindicacio': (['1.3', '1.5'], ['1.3', '1.6']),
 'RA1/activitats/a1-5-forum-amb-regles-d-acces':   (['1.2', '1.3'], ['1.2', '1.8']),
 'RA1/activitats/a1-6-actualitzar-protegir-i-copiar': (['1.5'], ['1.5', '1.7', '1.9', '1.10']),
 'RA1/practiques/p1-1-portal-wordpress':           (['1.1', '1.2', '1.3', '1.4', '1.5'], []),
 'RA2/teoria/t2-1-plataformes-d-aprenentatge':     (['2.1', '2.2'], ['2.3', '2.4']),
 'RA2/teoria/t2-2-un-moodle-per-dins':             (['2.2'], ['2.1', '2.2']),
 'RA2/teoria/t2-3-mantenir-un-moodle':             (['2.2'], ['2.5', '2.6', '2.7', '2.8']),
 'RA2/guies/g2-1-instal-lar-moodle':               (['2.2'], ['2.1']),
 'RA2/guies/g2-2-administrar-moodle':              (['2.2', '2.3'], ['2.2', '2.3', '2.4', '2.5', '2.6', '2.7', '2.8']),
 'RA2/activitats/a2-1-moodle-a-punt':              (['2.2'], ['2.1', '2.2']),
 'RA2/activitats/a2-2-cursos-usuaris-i-activitats': (['2.3'], ['2.3', '2.4']),
 'RA2/activitats/a2-3-copies-informes-i-seguretat': (['2.2'], ['2.5', '2.6', '2.7', '2.8']),
 'RA2/practiques/p2-1-portal-moodle':              (['2.1', '2.2', '2.3'], []),
 'RA3/teoria/t3-1-gestors-d-arxius-web':           (['3.1'], ['3.1', '3.2']),
 'RA3/teoria/t3-2-comptes-permisos-i-comparticio': (['3.2', '3.3'], ['3.4', '3.5']),
 'RA3/teoria/t3-3-trobar-ho-i-protegir-ho':        (['3.1'], ['3.6', '3.7', '3.8']),
 'RA3/guies/g3-1-instal-lar-nextcloud':            (['3.1'], ['3.3', '3.8']),
 'RA3/guies/g3-2-administrar-nextcloud':           (['3.1', '3.2', '3.3'], ['3.4', '3.5', '3.6', '3.7', '3.8']),
 'RA3/activitats/a3-1-el-nuvol-a-punt':            (['3.1'], ['3.1', '3.2', '3.3']),
 'RA3/activitats/a3-2-comptes-grups-i-recursos':   (['3.2', '3.3'], ['3.4', '3.5']),
 'RA3/activitats/a3-3-ordenar-trobar-i-protegir':  (['3.1'], ['3.5', '3.6', '3.7', '3.8']),
 'RA3/practiques/p3-1-nuvol-de-l-aula':            (['3.1', '3.2', '3.3'], []),
 'RA4/teoria/t4-1-ofimatica-web':                  (['4.1'], ['4.1', '4.2', '4.3']),
 'RA4/teoria/t4-2-treballar-hi-entre-diversos':    (['4.1'], ['4.6', '4.7']),
 'RA4/teoria/t4-3-comptes-permisos-i-seguretat':   (['4.2', '4.3'], ['4.4', '4.5']),
 'RA4/guies/g4-1-documents-fulls-i-formularis':    (['4.1'], ['4.3', '4.6', '4.7']),
 'RA4/guies/g4-2-presentacions-i-llocs-web':       (['4.1'], ['4.6', '4.7']),
 'RA4/activitats/a4-1-l-oficina-al-navegador':     (['4.1'], ['4.1', '4.2', '4.3']),
 'RA4/activitats/a4-2-document-full-i-formulari':  (['4.1'], ['4.6', '4.7']),
 'RA4/activitats/a4-3-comptes-permisos-i-seguretat': (['4.2', '4.3'], ['4.4', '4.5']),
 'RA4/practiques/p4-1-projecte-digital-del-grup':  (['4.1', '4.2', '4.3'], []),
 'RA5/teoria/t5-1-aplicacions-web-d-escriptori':   (['5.1'], ['5.1']),
 'RA5/teoria/t5-2-com-viatja-un-correu':           (['5.1'], ['5.3', '5.5']),
 'RA5/teoria/t5-3-calendaris-contactes-i-tasques': (['5.1'], ['5.6', '5.7']),
 'RA5/guies/g5-1-servidor-de-correu-intern':       (['5.1', '5.2'], ['5.3', '5.4']),
 'RA5/guies/g5-2-correu-web-amb-roundcube':        (['5.1', '5.2'], ['5.2', '5.3', '5.5']),
 'RA5/guies/g5-3-calendari-contactes-i-tasques':   (['5.1', '5.2'], ['5.6', '5.7']),
 'RA5/activitats/a5-1-busties-al-servidor':        (['5.1', '5.2'], ['5.3', '5.4']),
 'RA5/activitats/a5-2-correu-web':                 (['5.1', '5.2'], ['5.2', '5.3', '5.4', '5.5']),
 'RA5/activitats/a5-3-agenda-contactes-i-tasques': (['5.1', '5.2'], ['5.6', '5.7']),
 'RA5/practiques/p5-1-escriptori-web-de-l-organitzacio': (['5.1', '5.2'], []),
}

# Rúbrica de cada pràctica principal: (nom, pes al RA, [(apartat, criteris, punts)]).
# D'aquí surten el bloc «rúbrica» de la pàgina, els criteris del seu bloc de
# currículum i els criteris que exercita cada prova.
PRACTIQUES = {
 'RA1/practiques/p1-1-portal-wordpress': ('Pràctica P1.1', 60, [
   ("Requeriments comprovats i documentats abans d'instal·lar", ['1.1'], 0.5),
   ("Instal·lació: host virtual, base de dades MySQL, WordPress i enllaços permanents", ['1.1'], 1),
   ("Contingut: entrades, categories, pàgines, publicació programada i comentaris", ['1.3'], 1),
   ("Aparença: tema diferent, identitat del lloc i CSS addicional", ['1.3'], 1),
   ("Menús, ginys, sindicació i extensions configurades", ['1.6'], 1.5),
   ("Usuaris i grups amb rols diferents, provats amb intents fallits", ['1.2'], 1),
   ("Fòrum amb zona pública i zona restringida, amb regles d'accés", ['1.8'], 1),
   ("Actualitzacions aplicades i registrades", ['1.5'], 0.5),
   ("Mecanismes de seguretat del gestor activats i justificats", ['1.7'], 1),
   ("Còpia de seguretat completa i restauració provada", ['1.10'], 1),
   ("Llista de proves de funcionament passada abans i després dels canvis", ['1.4', '1.9'], 0.5),
 ]),
 'RA2/practiques/p2-1-portal-moodle': ('Pràctica P2.1', 60, [
   ("Instal·lació correcta i estructura del lloc i dels directoris explicada", ['2.1'], 1.5),
   ("Configuració inicial del lloc: nom, idioma, zona horària i normatives", ['2.2'], 1),
   ("Aparença personalitzada: tema, logotip, capçalera, peu i portada", ['2.2'], 1),
   ("Usuaris manuals i massius, grups i perfils personalitzats", ['2.3'], 1.5),
   ("Cursos amb els temes demanats, inscripcions i activació de funcionalitats", ['2.3'], 1),
   ("Comunicació provada: fòrum, consulta i missatgeria", ['2.4'], 1),
   ("Importació i exportació de cursos entre llocs", ['2.5'], 1),
   ("Còpia de seguretat del lloc i restauració provada", ['2.6'], 1),
   ("Informes d'accés i utilització interpretats", ['2.7'], 0.5),
   ("Seguretat del lloc comprovada i justificada", ['2.8'], 0.5),
 ]),
 'RA3/practiques/p3-1-nuvol-de-l-aula': ('Pràctica P3.1', 60, [
   ("Utilitat del servei justificada per a l'organització triada", ['3.1'], 0.5),
   ("Comparació raonada de dues aplicacions de gestió d'arxius web", ['3.2'], 1),
   ("Instal·lació i adaptació: requeriments, dades fora del web, límits i cron", ['3.3'], 2),
   ("Comptes classificats per permisos, grups i quotes, amb l'efecte demostrat", ['3.4'], 1.5),
   ("Jerarquia de carpetes, operacions amb fitxers i recursos compartits", ['3.5'], 1.5),
   ("Informació addicional: etiquetes, comentaris i descripcions de carpeta", ['3.6'], 1),
   ("Criteris d'indexació escrits, aplicats i demostrats amb cerques", ['3.7'], 1),
   ("Revisió de seguretat amb informe, còpia i restauració provada", ['3.8'], 1.5),
 ]),
 'RA4/practiques/p4-1-projecte-digital-del-grup': ('Pràctica P4.1', 60, [
   ("Utilitat de la suite justificada i aplicacions triades per a cada feina", ['4.1', '4.2'], 1),
   ("Entorn desplegat: carpetes, compartició, complements i document de treball", ['4.3'], 1),
   ("Presentació amb patró, notes i recursos citats", ['4.6'], 1.5),
   ("Enquesta: formulari amb tipus i validació, i finalitat explicada", ['4.6'], 1),
   ("Full de resultats amb fórmules, validació i gràfics", ['4.6'], 1.5),
   ("Informe escrit entre tots, amb estils, índex i gràfics enllaçats", ['4.7'], 1.5),
   ("Lloc web publicat amb les seccions i els documents incrustats", ['4.6'], 1),
   ("Taula d'accessos aplicada i comptes gestionats", ['4.4'], 0.75),
   ("Seguretat: dos passos, restriccions i auditoria de comparticions", ['4.5'], 0.75),
 ]),
 'RA5/practiques/p5-1-escriptori-web-de-l-organitzacio': ('Pràctica P5.1', 60, [
   ("Comparació i descripció de les aplicacions web d'escriptori triades", ['5.1'], 1),
   ("Servidor de correu intern instal·lat, amb bústies i ports comprovats", ['5.2'], 1.5),
   ("Correu web instal·lat i integrat amb el servidor de correu", ['5.2', '5.3'], 2),
   ("Comptes, àlies, altes i baixes documentats i provats", ['5.4'], 1.5),
   ("Accés al correu verificat entre comptes, amb filtres i contactes", ['5.5'], 1.5),
   ("Calendari web instal·lat, amb calendaris i comparticions", ['5.6'], 1.5),
   ("Prestacions demostrades: cites, repeticions, convidats, tasques i sincronització", ['5.7'], 1),
 ]),
}


def _ordena(codis):
    return sorted(set(codis), key=lambda x: tuple(map(int, x.split('.'))))


for _k, (_n, _pes, _files) in PRACTIQUES.items():
    assert abs(sum(f[2] for f in _files) - 10) < 1e-9, f'{_k}: la rúbrica no suma 10'
    MAP[_k] = (MAP[_k][0], _ordena(c for f in _files for c in f[1]))

PROVA = {nom: _ordena(c for f in files for c in f[1])
         for nom, _, files in PRACTIQUES.values()}


def pagines_de(codi, contingut=False):
    """Codis de les pàgines que treballen un criteri (o un contingut)."""
    out = []
    for key, parell in MAP.items():
        if codi not in parell[0 if contingut else 1]:
            continue
        m = re.match(r'([tgap])(\d+)-(\d+)', key.rsplit('/', 1)[1])
        out.append(f'{m.group(1).upper()}{m.group(2)}.{m.group(3)}')
    return out


EXAMEN = 'Examen tipus test'


def instrument(ca):
    """Amb què es qualifica un criteri: la pràctica del RA i l'examen.

    La nota de cada RA són dues coses: la pràctica principal (60 %) i un
    examen tipus test a Moodle (40 %), que abasta tot el RA. Les activitats
    no tenen pes: són l'assaig de la pràctica i es comenten amb la rúbrica
    de seguiment. Un criteri que la pràctica no exercita només s'avalua a
    l'examen, i això es veu a la matriu.
    """
    proves = [nom for nom, cas in PROVA.items() if ca in cas]
    return ' · '.join(proves + [EXAMEN])


BLOCK_RE = re.compile(
    r'\n*<!-- =+ CURRÍCULUM =+ -->\n<div class="cq-block" data-kind="currículum">.*?\n</div>\n',
    re.S)
ANCHOR = '<!-- === PEU DE NAVEGACIÓ INICI === -->'


def block(cont, crit):
    rows = []
    for c in cont:
        rows.append(f'  <p><span class="lbl">Contingut {c}</span> {CONT[c]}</p>')
    for c in crit:
        rows.append(f'  <p><span class="lbl">CA {c}</span> {CA[c]}</p>')
    return ('\n<!-- ============ CURRÍCULUM ============ -->\n'
            '<div class="cq-block" data-kind="currículum">\n'
            '  <h2>Al currículum</h2>\n' + '\n'.join(rows) + '\n</div>\n')


RA_NOM = {
 '1': 'Gestors de continguts',
 '2': "Sistemes de gestió d'aprenentatge",
 '3': "Serveis de gestió d'arxius web",
 '4': "Aplicacions d'ofimàtica web",
 '5': "Aplicacions web d'escriptori",
}


def etiqueta(key):
    """RA5/activitats/a5-2-dos-llocs → A5.2, i el títol curt del fitxer."""
    nom = key.rsplit('/', 1)[1]
    num = re.match(r'([TGAP])(\d+)-(\d+)', nom.upper())
    codi = f'{num.group(1)}{num.group(2)}.{num.group(3)}' if num else nom
    titol = re.search(r'<header class="cq-header">.*?<h1>(.*?)</h1>',
                      (ARREL / (key + '.html')).read_text(), re.S)
    t = re.sub(r'<[^>]+>', '', titol.group(1)).strip() if titol else ''
    return codi, _html.escape(t)


def matriu():
    """Regenera cobertura.html: cada CA i cada contingut, amb qui el treballa."""
    per_ca, per_cont = {}, {}
    for key, (cont, crit) in MAP.items():
        codi, titol = etiqueta(key)
        for c in crit:
            per_ca.setdefault(c, []).append((codi, titol))
        for c in cont:
            per_cont.setdefault(c, []).append((codi, titol))

    css = re.search(r'/\* === SINAPSI-CSS INICI.*?/\* === SINAPSI-CSS FI[^\n]*\n',
                    (ARREL / 'index.html').read_text(), re.S).group(0)

    out = ['<!DOCTYPE html>', '<html lang="ca">', '<head>',
           '<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           '<title>Cobertura del currículum — 0228 Aplicacions web</title>',
           '<style>', css, '</style>', '</head>', '<body>',
           '<header class="cq-header">',
           '  <div class="eyebrow">CFGM SMX · Mòdul 0228 · ús intern</div>',
           '  <h1>Cobertura del currículum</h1>',
           '  <p class="lede">Cada criteri d\'avaluació i cada contingut del '
           'currículum de la Generalitat, amb les pàgines que el treballen. '
           'Document de programació: no es publica al web de l\'alumnat.</p>',
           '</header>']

    sense, nomes_rubrica, forans = [], [], []
    for ra in sorted(RA_NOM):
        cas = [c for c in CA if c.split('.')[0] == ra]
        conts = [c for c in CONT if c.split('.')[0] == ra]
        out += [f'\n<div class="cq-block" data-kind="RA{ra}">',
                f'  <h2>RA{ra} · {RA_NOM[ra]}</h2>',
                '  <div class="cq-tablewrap"><table class="cq-table">',
                '    <thead><tr><th>Criteri</th><th>Enunciat</th>'
                '<th>On es treballa</th><th>Instrument</th></tr></thead><tbody>']
        for c in cas:
            pags = per_ca.get(c, [])
            if not pags:
                sense.append(c)
            cel = ' · '.join(f'{k}' for k, _ in pags) or \
                  '<strong>sense cobrir</strong>'
            # Criteri que només es treballa fora del seu NF: l'evidència val
            # igualment per a aquest RA, que és qui el qualifica.
            if pags and all(k[1] != ra for k, _ in pags):
                forans.append(c)
                cel += (f' <em>(fora del NF{ra}; l\'evidència s\'utilitza per '
                        f'avaluar el RA{ra})</em>')
            inst = instrument(c)
            if not inst.startswith('Pràctica'):
                nomes_rubrica.append(c)
                inst = f'<em>{inst}</em>'
            out.append(f'    <tr><td><code>{c}</code></td>'
                       f'<td>{_html.escape(CA[c])}</td><td>{cel}</td>'
                       f'<td>{inst}</td></tr>')
        for c in conts:
            pags = per_cont.get(c, [])
            cel = ' · '.join(k for k, _ in pags) or '<strong>sense cobrir</strong>'
            out.append(f'    <tr><td><code>C {c}</code></td>'
                       f'<td>{_html.escape(CONT[c])}</td><td>{cel}</td>'
                       f'<td>—</td></tr>')
        if not cas and not conts:
            out.append('    <tr><td colspan="4"><strong>El mòdul encara no '
                       'té material d\'aquest resultat d\'aprenentatge.'
                       '</strong></td></tr>')
        out += ['    </tbody></table></div>', '</div>']

    out += ['\n<div class="cq-block" data-kind="proves">',
            '  <h2>Què exercita cada pràctica</h2>',
            '  <p>La nota de cada RA és la pràctica principal (60 %), '
            'corregida amb demostració en directe i README, i un examen tipus '
            'test a Moodle (40 %) que abasta tot el RA. Les activitats no '
            'tenen pes. Aquesta taula documenta què posa a prova cada '
            'pràctica; la resta de criteris queden per a l\'examen.</p>',
            '  <div class="cq-tablewrap"><table class="cq-table">',
            '    <thead><tr><th>Pràctica</th><th>Criteris que exercita</th>'
            '</tr></thead><tbody>']
    for nom, cas in PROVA.items():
        out.append(f'    <tr><td>{nom}</td>'
                   f'<td>{" · ".join(f"<code>{c}</code>" for c in cas)}</td></tr>')
    out += ['    </tbody></table></div>', '</div>',
            '\n<div class="cq-block" data-kind="resum">',
            '  <h2>Què queda per cobrir</h2>',
            '  <p>Criteris sense cap pàgina: ' +
            (', '.join(f'<code>{c}</code>' for c in sorted(sense)) or 'cap') +
            '.</p>',
            '  <p>Criteris que cap pràctica no exercita i que, per tant, '
            '<strong>només es qualifiquen a l\'examen</strong>: ' +
            (', '.join(f'<code>{c}</code>' for c in sorted(
                nomes_rubrica,
                key=lambda x: tuple(map(int, x.split('.'))))) or 'cap') +
            '. Les preguntes de l\'examen d\'aquell RA els han de cobrir.</p>',
            '  <p>Criteris que només es treballen fora del seu nucli formatiu: ' +
            (', '.join(f'<code>{c}</code>' for c in sorted(
                forans, key=lambda x: tuple(map(int, x.split('.'))))) or 'cap') +
            '. L\'evidència s\'utilitza per avaluar-los al RA que els conté.</p>',
            '</div>', '</body>', '</html>']

    sortida = pathlib.Path(__file__).with_name('cobertura.html')
    sortida.write_text('\n'.join(out) + '\n')
    print(f'{sortida}  ·  {len(sense)} criteris sense cobrir  ·  '
          f'{len(nomes_rubrica)} només a l\'examen  ·  '
          f'{len(forans)} fora del seu NF')


def punts(x):
    return f'{x:g}'.replace('.', ',')


RUB_RE = re.compile(
    r'\n*<!-- =+ RÚBRICA =+ -->\n<div class="cq-block" data-kind="rúbrica">.*?\n</div>\n',
    re.S)


def rubrica(key):
    """Bloc «rúbrica» d'una pràctica final: apartats, criteris i punts."""
    nom, pes, files = PRACTIQUES[key]
    rows = '\n'.join(
        f'        <tr><td>{a}</td><td>{" · ".join(f"<code>{c}</code>" for c in cas)}</td>'
        f'<td>{punts(pt)}</td></tr>' for a, cas, pt in files)
    return ('\n<!-- ============ RÚBRICA ============ -->\n'
            '<div class="cq-block" data-kind="rúbrica">\n'
            '  <h2>Com es qualifica</h2>\n'
            f'  <p>Aquesta pràctica és el {pes} % de la nota del {key.split("/")[0]}; '
            f'l\'altre {100 - pes} % és l\'examen tipus test. Cada apartat '
            'es puntua a la demostració i amb les evidències del README: la '
            'puntuació sencera si funciona, la meitat si funciona amb mancances '
            'i zero si no es pot demostrar.</p>\n'
            '  <div class="cq-tablewrap">\n    <table class="cq-table">\n'
            '      <thead><tr><th>Apartat</th><th>Criteri</th><th>Punts</th></tr></thead>\n'
            f'      <tbody>\n{rows}\n'
            '        <tr><td><strong>Total</strong></td><td></td><td><strong>10</strong></td></tr>\n'
            '      </tbody>\n    </table>\n  </div>\n</div>\n')


IDX_RE = re.compile(r'<!-- === CURRÍCULUM DEL RA INICI === -->.*?'
                    r'<!-- === CURRÍCULUM DEL RA FI === -->', re.S)


def avalua(ca):
    """Instruments d'un criteri al quadre del RA: la pràctica i l'examen."""
    return instrument(ca)


def index_ra(ra):
    """Bloc «Al currículum» de RAn/index.html: RA, criteris i continguts."""
    p = ARREL / f'RA{ra}' / 'index.html'
    if not p.exists():
        return
    def on(codi, cont=False):
        return ' · '.join(pagines_de(codi, cont)) or '<strong>sense cobrir</strong>'
    f_ca = '\n'.join(
        f'        <tr><td><code>{c}</code></td><td>{_html.escape(CA[c])}</td>'
        f'<td>{on(c)}</td><td>{avalua(c)}</td></tr>'
        for c in CA if c.split('.')[0] == ra)
    f_co = '\n'.join(
        f'        <tr><td><code>{c}</code></td><td>{_html.escape(CONT[c])}</td>'
        f'<td>{on(c, True)}</td></tr>'
        for c in CONT if c.split('.')[0] == ra)
    bloc = ('<!-- === CURRÍCULUM DEL RA INICI === -->\n'
            '<div class="cq-block" data-kind="currículum">\n'
            '  <h2>Al currículum</h2>\n'
            f'  <p><span class="lbl">RA{ra}</span> {_html.escape(RA[ra])}</p>\n'
            '  <div class="cq-tablewrap">\n    <table class="cq-table">\n'
            '      <thead><tr><th>Criteri</th><th>Enunciat</th>'
            '<th>On es treballa</th><th>Com s\'avalua</th></tr></thead>\n'
            f'      <tbody>\n{f_ca}\n      </tbody>\n    </table>\n  </div>\n'
            '  <div class="cq-tablewrap">\n    <table class="cq-table">\n'
            '      <thead><tr><th>Contingut</th><th>Enunciat</th>'
            '<th>On es treballa</th></tr></thead>\n'
            f'      <tbody>\n{f_co}\n      </tbody>\n    </table>\n  </div>\n'
            '</div>\n'
            '<!-- === CURRÍCULUM DEL RA FI === -->')
    s = p.read_text()
    if not IDX_RE.search(s):
        print('SENSE MARCADORS DE CURRÍCULUM:', p)
        return
    p.write_text(IDX_RE.sub(lambda m: bloc, s))


def main():
    n = 0
    for ra in RA_NOM:
        index_ra(ra)
    for key, (cont, crit) in MAP.items():
        if '/guies/' in key:
            continue
        p = ARREL / (key + '.html')
        s = p.read_text()
        s = BLOCK_RE.sub('\n', s)
        s = RUB_RE.sub('\n', s)
        if key in PRACTIQUES and ANCHOR in s:
            s = s.replace(ANCHOR, rubrica(key) + '\n' + ANCHOR, 1)
        if ANCHOR not in s:
            print('SENSE ÀNCORA:', p)
            continue
        s = s.replace(ANCHOR, block(cont, crit) + '\n' + ANCHOR, 1)
        p.write_text(s)
        n += 1
    print(f'{n} pàgines amb bloc de currículum')


if __name__ == '__main__':
    main()
    if '--matriu' in sys.argv:
        matriu()
