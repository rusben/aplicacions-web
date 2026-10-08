#!/usr/bin/env python3
"""Editor visual del material: edita qualsevol pàgina del mòdul al navegador,
sense codi.

    python3 editor.py

Obre http://localhost:8765 i tria una pàgina, agrupada per RA i secció. Cada
bloc s'edita com un document: clica-hi i escriu. La barra de cada bloc permet
canviar-ne l'etiqueta, moure'l, duplicar-lo o esborrar-lo, i n'indica el
nombre de mots per vigilar la densitat (90–135 per bloc).

Els canvis van al fitxer .html real. El CSS i el motor del quiz no es toquen
mai. Abans de cada desada es guarda una còpia a _copies/ (a l'arrel) i
després es regenera la web de revisió del RA corresponent i es torna a
passar revisa.py sobre aquell RA.
"""
import html, http.server, json, pathlib, re, shutil
import socketserver, subprocess, sys, urllib.parse
from datetime import datetime

import revisa   # la regla de densitat és seva; aquí només es consulta

PORT = 8765
ROOT = pathlib.Path(__file__).resolve().parent
COPIES = ROOT / '_copies'

# Etiquetes en ús al mòdul. Se'n pot escriure una de nova des del navegador.
KINDS = ['objectius', 'teoria', 'referència', 'exemple', 'cas real',
         'escenari', 'enunciat',
         'pas a pas', 'recordatori', 'observació', 'bones pràctiques',
         'problemes', 'comprovació', 'resum', 'lliurament', 'currículum',
         'quiz']


# ---------------------------------------------------------------- pàgines

def ra_folders():
    """Les carpetes RA*, ordenades."""
    return sorted(p for p in ROOT.glob('RA*') if p.is_dir())


def pages():
    """Totes les pàgines editables, en l'ordre de navegació: portal, i per
    a cada RA, la seva portada, teoria, guies, activitats i pràctiques."""
    found = []
    if (ROOT / 'index.html').exists():
        found.append('index.html')
    for ra in ra_folders():
        if (ra / 'index.html').exists():
            found.append(str((ra / 'index.html').relative_to(ROOT)))
        for folder in ('teoria', 'guies', 'activitats', 'practiques'):
            found += sorted(str(p.relative_to(ROOT)) for p in (ra / folder).glob('*.html'))
    return found


def resolve(rel):
    """Camí absolut d'una pàgina, comprovant que no s'escapa de la llista
    de pàgines editables (evita path traversal i tocar _identitat/docs/etc)."""
    if rel not in pages():
        raise ValueError(f'pàgina no editable: {rel}')
    return ROOT / rel


def ra_of(rel):
    """Nom de la carpeta RA a la qual pertany la pàgina, o None (portal)."""
    parts = pathlib.Path(rel).parts
    return parts[0] if len(parts) > 1 and parts[0].startswith('RA') else None


# ------------------------------------------------- trobar els blocs al font

OPEN_BLOCK = re.compile(r'<div class="cq-block" data-kind="([^"]*)"[^>]*>')
DIV_TAG = re.compile(r'</?div\b')


def blocks(src):
    """Per a cada bloc: (etiqueta, inici del contingut, final del contingut)."""
    out = []
    for m in OPEN_BLOCK.finditer(src):
        depth, pos = 1, m.end()
        while depth:
            t = DIV_TAG.search(src, pos)
            if not t:
                raise ValueError('hi ha un <div> sense tancar al fitxer')
            depth += -1 if t.group().startswith('</') else 1
            pos = t.end()
        out.append((m.group(1), m.end(), t.start()))
    return out


def header_span(src):
    """Tram editable de la capçalera, o None si la pàgina no en té."""
    m = re.search(r'<header class="cq-header">', src)
    return (m.end(), src.index('</header>', m.end())) if m else None


# --------------------------------------------------------- resum per llista

def plain(fragment):
    """Text pla d'un fragment d'HTML."""
    return html.unescape(re.sub(r'<[^>]+>', '', fragment)).strip()


def page_ref(rel, src):
    """Referència curta de la pàgina (T2.3, G1.1, A4.2...) per mostrar-la.

    Les portades no en tenen: hi posem «Índex», que és el que són."""
    if len(pathlib.Path(rel).parts) < 3:
        return 'Índex'
    m = re.search(r'<title>\s*([^·<]+?)\s*·', src)
    return m.group(1).strip() if m else '?'


def page_title(rel, src):
    """Títol de la pàgina.

    A les portades val el subtítol: els seus H1 diuen tots «Aplicacions Web»
    i no distingirien res."""
    if len(pathlib.Path(rel).parts) < 3:
        m = re.search(r'<p class="lede">(.*?)</p>', src, re.S)
        if m:
            return plain(m.group(1))
    m = re.search(r'<h1>(.*?)</h1>', src, re.S)
    return plain(m.group(1)) if m else '(sense títol)'


def page_summary(rel):
    """(ref, títol, n. de blocs, hi ha algun bloc massa llarg?) d'una pàgina."""
    src = resolve(rel).read_text(encoding='utf-8')
    found = blocks(src)
    over = any(kind in revisa.DENSE
               and len(revisa.text_of(src[start:end]).split()) > revisa.MAX_WORDS
               for kind, start, end in found)
    return page_ref(rel, src), page_title(rel, src), len(found), over


SECTIONS = {'teoria': 'Teoria', 'guies': 'Guies', 'activitats': 'Activitats',
            'practiques': 'Pràctiques'}


def section_of(rel):
    """Nom de secció per agrupar a la portada, o None per a les portades."""
    parts = pathlib.Path(rel).parts
    if len(parts) < 2:
        return None
    return SECTIONS.get(parts[1])


# ------------------------------------------------------------- neteja

def clean(fragment):
    """Treu del fragment el que hi hagi deixat el navegador o el quiz."""
    f = fragment
    f = re.sub(r'<div class="ed-tools".*?</div>\s*(?=<|$)', '', f, flags=re.S)
    f = re.sub(r'\s+(contenteditable|spellcheck)="[^"]*"', '', f)
    f = re.sub(r'\s+class="cq-option (cq-selected|cq-correct|cq-incorrect)"',
               ' class="cq-option"', f)
    f = re.sub(r'\s+class="cq-feedback (ok|ko)"', ' class="cq-feedback"', f)
    f = re.sub(r'(<button[^>]*?)\s+disabled(?:="[^"]*")?', r'\1', f)
    f = re.sub(r'(<div class="cq-feedback">)[^<]*(</div>)', r'\1\2', f)
    f = re.sub(r'[ \t]+$', '', f, flags=re.M)
    return '\n' + f.strip('\n') + '\n'


def indent(fragment):
    """Sagna un fragment nou perquè el font es continuï llegint bé."""
    lines = [l for l in fragment.strip('\n').split('\n')]
    if all(l.startswith('  ') or not l.strip() for l in lines):
        return '\n' + '\n'.join(lines) + '\n'
    return '\n' + '\n'.join(('  ' + l).rstrip() for l in lines) + '\n'


# ------------------------------------------------------------- desar

def save(rel, header, incoming):
    """Desa la pàgina. `incoming` és una llista de {kind, html}.

    Si l'estructura no ha canviat (mateixos blocs i mateix ordre) només se'n
    substitueix el contingut, i el fitxer queda igual byte a byte allà on no
    has tocat res. Si has mogut, afegit o esborrat blocs, es reconstrueix el
    cos de la pàgina sencer.

    Després escriu una còpia de seguretat, regenera la web de revisió del RA
    i torna a passar revisa.py sobre aquell RA. Retorna el missatge a mostrar.
    """
    path = resolve(rel)
    src = path.read_text(encoding='utf-8')
    current = blocks(src)

    COPIES.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    safe_name = rel.replace('/', '__')
    shutil.copy2(path, COPIES / f'{safe_name}.{stamp}.html')

    same = [k for k, _, _ in current] == [b['kind'] for b in incoming]
    if same:
        spans = [(s, e) for _, s, e in current]
        frags = [clean(b['html']) for b in incoming]
        for (start, end), frag in sorted(zip(spans, frags), reverse=True):
            src = src[:start] + frag + src[end:]
    else:
        body = []
        for b in incoming:
            kind = b['kind'].strip() or 'teoria'
            rule = '=' * max(4, 40 - len(kind))
            body.append(f'<!-- {rule} {kind.upper()} {rule} -->\n'
                        f'<div class="cq-block" data-kind="{kind}">'
                        f'{indent(clean(b["html"]))}</div>')
        start = src.index('<div class="cq-block"')
        before = src[:start].rstrip()
        if before.endswith('-->'):          # el comentari que encapçala el bloc
            start = before.rindex('<!--')
        end = current[-1][2] + len('</div>')
        src = src[:start] + '\n\n'.join(body) + src[end:]

    if header is not None:
        span = header_span(src)
        if span:
            src = src[:span[0]] + clean(header) + src[span[1]:]

    path.write_text(src, encoding='utf-8')
    return revalidate(rel)


def revalidate(rel):
    """Regenera la web de revisió del RA de `rel` i torna a passar revisa.py.
    Retorna un missatge curt per a la barra de l'editor."""
    ra = ra_of(rel)
    if ra is None:
        return 'Portal desat.'

    notes = []
    web = ROOT / 'fes-web.py'
    if web.exists():
        r = subprocess.run([sys.executable, str(web), ra], capture_output=True, text=True)
        out = (r.stdout or r.stderr).strip().splitlines()
        if out:
            notes.append(out[-1])

    r = subprocess.run([sys.executable, str(ROOT / 'revisa.py'), ra],
                       capture_output=True, text=True)
    out = (r.stdout or r.stderr).strip().splitlines()
    if out:
        notes.append(out[-1])
    return '  ·  '.join(notes)


# ------------------------------------------------------------- pàgines HTML

INDEX = """<!DOCTYPE html><html lang="ca"><head><meta charset="utf-8">
<title>Editor del material</title>
<style>
  body {{ margin:0; padding:40px 20px 60px; background:#E7ECF2; color:#212E3A;
         font:16px/1.5 -apple-system,"Segoe UI",Roboto,sans-serif; }}
  main {{ max-width:760px; margin:0 auto; }}
  h1 {{ font-size:1.5rem; margin:0 0 4px; }}
  p.lead {{ color:#5F6E7D; margin:0 0 28px; }}
  h2 {{ font-size:1.05rem; margin:32px 0 4px; color:#16202C; }}
  p.ra-lede {{ color:#5F6E7D; margin:0 0 12px; font-size:.9rem; }}
  h3 {{ font-size:.8rem; text-transform:uppercase; letter-spacing:.04em;
        color:#8A98A6; margin:16px 0 6px; }}
  ul {{ list-style:none; margin:0; padding:0; }}
  li {{ margin-bottom:6px; }}
  a {{ display:flex; align-items:baseline; gap:10px; padding:10px 14px;
       background:#FFF; border:1px solid #D3DDE7; border-radius:8px;
       color:#212E3A; text-decoration:none; }}
  a:hover {{ border-color:#1D4E89; }}
  .ref {{ font-weight:700; color:#1D4E89; min-width:44px; }}
  .ttl {{ flex:1; }}
  .meta {{ color:#8A98A6; font-size:.82rem; white-space:nowrap; }}
  .warn {{ color:#C2410C; font-weight:600; font-size:.82rem; white-space:nowrap; }}
</style></head><body><main>
<h1>Editor del material</h1>
<p class="lead">Tria una pàgina. Els canvis es desen al fitxer real i es fa una còpia abans.</p>
{groups}
</main></body></html>"""

GROUP = """<h2>{ra}</h2>
<p class="ra-lede">{lede}</p>
{sections}"""

SECTION = """<h3>{name}</h3>
<ul>
{items}
</ul>"""

ITEM = """<li><a href="/edit?f={href}">
  <span class="ref">{ref}</span><span class="ttl">{title}</span>
  {extra}
</a></li>"""


def render_index():
    all_pages = pages()

    def item(rel):
        ref, title, n, over = page_summary(rel)
        extra = '<span class="warn">bloc llarg</span>' if over else ''
        extra += f'<span class="meta">{n} {"bloc" if n == 1 else "blocs"}</span>'
        return ITEM.format(href=urllib.parse.quote(rel), ref=html.escape(ref),
                           title=html.escape(title), extra=extra)

    groups = []
    if 'index.html' in all_pages:
        groups.append(SECTION.format(name='Portal', items=item('index.html')))

    for ra in ra_folders():
        name = ra.name
        ra_pages = [p for p in all_pages if ra_of(p) == name]
        if not ra_pages:
            continue
        idx = [p for p in ra_pages if pathlib.Path(p).parts[1] == 'index.html']
        lede_m = re.search(r'class="lede">([^<]*)',
                           (ra / 'index.html').read_text(encoding='utf-8')) if idx else None
        lede = lede_m.group(1) if lede_m else ''
        sections = []
        if idx:
            sections.append(SECTION.format(name='Portada', items=item(idx[0])))
        for label in SECTIONS.values():
            group_pages = [p for p in ra_pages if section_of(p) == label]
            if group_pages:
                sections.append(SECTION.format(
                    name=label, items='\n'.join(item(p) for p in group_pages)))
        groups.append(GROUP.format(ra=name, lede=html.escape(lede),
                                   sections='\n'.join(sections)))

    return INDEX.format(groups='\n'.join(groups))


BAR = """
<style>
  .ed-bar {{ position:fixed; top:0; left:0; right:0; z-index:9999;
    display:flex; align-items:center; gap:10px; padding:8px 14px;
    background:#16202C; color:#C7D4E1; font:13px/1.4 -apple-system,sans-serif; }}
  .ed-bar a, .ed-bar label {{ color:#74A9E4; text-decoration:none; cursor:pointer; }}
  .ed-bar a.off {{ color:#4A5A6B; pointer-events:none; }}
  .ed-bar select {{ background:#0E1620; color:#C7D4E1; border:1px solid #2C3A49;
    border-radius:5px; padding:4px 6px; font:inherit; max-width:260px; }}
  .ed-bar .grow {{ flex:1; text-align:right; color:#8FA1B4; }}
  .ed-bar button {{ padding:6px 16px; border:none; border-radius:6px;
    background:#1D4E89; color:#FFF; font:inherit; font-weight:600; cursor:pointer; }}
  .ed-bar button:disabled {{ background:#3A4A5C; cursor:default; }}
  body {{ padding-top:52px !important; }}
  body.ed-mobile .cq-block, body.ed-mobile .cq-header {{ max-width:343px; }}
  /* La navegació la genera aplica.py: aquí no s'edita i xocaria amb la barra. */
  .cq-nav, .cq-pager {{ display:none !important; }}

  .cq-block[contenteditable="true"] {{ padding-right:34px; }}
  .cq-block[contenteditable="true"]:hover {{ outline:1px dashed #B3C2D2; outline-offset:4px; }}
  .cq-block[contenteditable="true"]:focus, .cq-header[contenteditable="true"]:focus {{
    outline:2px solid #1D4E89; outline-offset:4px; }}
  .ed-tools {{ position:absolute; top:6px; right:6px; display:flex; align-items:center;
    gap:2px; opacity:0; transition:opacity .12s; font:11px/1 -apple-system,sans-serif; }}
  .cq-block:hover .ed-tools, .cq-block:focus-within .ed-tools {{ opacity:1; }}
  .ed-tools button {{ width:22px; height:22px; padding:0; border:1px solid #DCE7F3;
    border-radius:5px; background:#FFF; color:#1D4E89; cursor:pointer; font-size:12px; }}
  .ed-tools button:hover {{ background:#EFF5FB; }}
  .ed-tools .ed-kind {{ border:1px solid #DCE7F3; border-radius:5px; background:#FFF;
    color:#5C6875; font:11px -apple-system,sans-serif; padding:3px 4px; max-width:130px; }}
  .ed-tools .ed-words {{ color:#8A98A6; padding:0 4px; white-space:nowrap; }}
  .ed-tools .ed-words.over {{ color:#C2410C; font-weight:700; }}
  .ed-add {{ display:block; width:660px; max-width:100%; margin:-8px auto 18px;
    border:1px dashed #C6D2DE; border-radius:6px; background:transparent;
    color:#8A98A6; font:12px -apple-system,sans-serif; padding:4px; cursor:pointer; }}
  .ed-add:hover {{ border-color:#1D4E89; color:#1D4E89; }}
  @media print {{ .ed-bar, .ed-tools, .ed-add {{ display:none !important; }} }}
</style>
<div class="ed-bar">
  <a href="/">&larr; pàgines</a>
  <a id="ed-prev" title="Pàgina anterior">&#8249;</a>
  <select id="ed-goto">{options}</select>
  <a id="ed-next" title="Pàgina següent">&#8250;</a>
  <label><input type="checkbox" id="ed-mob"> 375&nbsp;px</label>
  <span class="grow" id="ed-status">Clica sobre qualsevol text i escriu.</span>
  <button id="ed-save" disabled>Desa</button>
</div>
<script>
(function () {{
  var rel = {rel_json}, kinds = {kinds_json}, list = {pages_json};
  var status = document.getElementById('ed-status');
  var saveBtn = document.getElementById('ed-save');
  var header = document.querySelector('.cq-header');
  var dirty = false;

  try {{ document.execCommand('defaultParagraphSeparator', false, 'p'); }} catch (e) {{}}

  function touched() {{
    dirty = true;
    saveBtn.disabled = false;
    status.textContent = 'Canvis sense desar.';
  }}

  // ---- comptador de mots: només la prosa, sense codi ni taules ni test
  function countWords(block) {{
    var c = block.cloneNode(true);
    [].forEach.call(c.querySelectorAll('pre, table, .cq-question, .dora-flow, .ed-tools'),
      function (n) {{ n.remove(); }});
    return (c.textContent.trim().match(/\\S+/g) || []).length;
  }}

  function refresh(block) {{
    var n = countWords(block);
    var w = block.querySelector('.ed-words');
    w.textContent = n + ' mots';
    var dens = block.dataset.kind && {dense_json}.indexOf(block.dataset.kind) >= 0;
    w.className = 'ed-words' + (dens && n > {max_words} ? ' over' : '');
    w.title = dens ? 'Densitat recomanada: 90–{max_words} mots per bloc.'
                   : 'Aquest tipus de bloc no té límit de densitat.';
  }}

  // ---- barra de cada bloc
  function equip(block) {{
    if (block.querySelector('.ed-tools')) return;
    block.contentEditable = 'true';
    block.spellcheck = true;
    block.addEventListener('input', function () {{ touched(); refresh(block); }});

    var tools = document.createElement('div');
    tools.className = 'ed-tools';
    tools.contentEditable = 'false';

    var words = document.createElement('span');
    words.className = 'ed-words';
    tools.appendChild(words);

    var sel = document.createElement('select');
    sel.className = 'ed-kind';
    sel.title = 'Etiqueta del bloc';
    var here = block.dataset.kind;
    kinds.concat(kinds.indexOf(here) < 0 ? [here] : []).forEach(function (k) {{
      var o = document.createElement('option');
      o.value = o.textContent = k;
      if (k === here) o.selected = true;
      sel.appendChild(o);
    }});
    var other = document.createElement('option');
    other.value = '__nova__';
    other.textContent = 'etiqueta nova...';
    sel.appendChild(other);
    sel.addEventListener('change', function () {{
      var v = sel.value;
      if (v === '__nova__') {{
        v = (prompt('Etiqueta nova:', here) || here).trim();
        var o = document.createElement('option');
        o.value = o.textContent = v;
        sel.insertBefore(o, other);
      }}
      block.dataset.kind = v;
      here = v;
      sel.value = v;
      touched();
    }});
    tools.appendChild(sel);

    [['\\u2191', 'Puja el bloc', function () {{
        var p = block.previousElementSibling;
        while (p && !p.classList.contains('cq-block')) p = p.previousElementSibling;
        if (p) {{ p.parentNode.insertBefore(block, p); touched(); }}
      }}],
     ['\\u2193', 'Baixa el bloc', function () {{
        var n = block.nextElementSibling;
        while (n && !n.classList.contains('cq-block')) n = n.nextElementSibling;
        if (n) {{ n.parentNode.insertBefore(block, n.nextSibling); touched(); }}
      }}],
     ['\\u29C9', 'Duplica el bloc', function () {{
        var copy = block.cloneNode(true);
        copy.querySelector('.ed-tools').remove();
        block.parentNode.insertBefore(copy, block.nextSibling);
        equip(copy); refresh(copy); touched();
      }}],
     ['\\u2715', 'Esborra el bloc', function () {{
        if (confirm('Esborrar aquest bloc?')) {{ block.remove(); touched(); }}
      }}]
    ].forEach(function (b) {{
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = b[0];
      btn.title = b[1];
      btn.addEventListener('click', b[2]);
      tools.appendChild(btn);
    }});

    block.appendChild(tools);
    refresh(block);
  }}

  function all() {{
    return [].slice.call(document.querySelectorAll('.cq-block'));
  }}

  if (header) {{
    header.contentEditable = 'true';
    header.addEventListener('input', touched);
  }}
  all().forEach(equip);

  // ---- afegir un bloc al final
  var add = document.createElement('button');
  add.className = 'ed-add';
  add.textContent = '+ bloc nou al final';
  add.addEventListener('click', function () {{
    var b = document.createElement('div');
    b.className = 'cq-block';
    b.dataset.kind = 'teoria';
    b.innerHTML = '<h2>Títol del bloc</h2>\\n  <p>Escriu-hi el text.</p>';
    add.parentNode.insertBefore(b, add);
    equip(b); touched(); b.focus();
  }});
  document.body.appendChild(add);

  // ---- navegació entre pàgines
  var i = list.indexOf(rel);
  var goTo = function (r) {{
    if (dirty && !confirm('Tens canvis sense desar. Vols sortir igualment?')) return;
    dirty = false;
    location.href = '/edit?f=' + encodeURIComponent(r);
  }};
  document.getElementById('ed-goto').addEventListener('change', function (e) {{
    goTo(e.target.value);
  }});
  var prev = document.getElementById('ed-prev'), next = document.getElementById('ed-next');
  if (i > 0) prev.addEventListener('click', function () {{ goTo(list[i - 1]); }});
  else prev.className = 'off';
  if (i < list.length - 1) next.addEventListener('click', function () {{ goTo(list[i + 1]); }});
  else next.className = 'off';

  document.getElementById('ed-mob').addEventListener('change', function (e) {{
    document.body.classList.toggle('ed-mobile', e.target.checked);
  }});

  // En mode edició el quiz no ha de reaccionar als clics.
  document.addEventListener('click', function (e) {{
    if (e.target.closest('.cq-option, .cq-check-btn')) {{
      e.preventDefault();
      e.stopPropagation();
    }}
  }}, true);

  // ---- desar
  function send() {{
    saveBtn.disabled = true;
    status.textContent = 'Desant...';
    var payload = {{
      f: rel,
      header: header ? header.innerHTML : null,
      blocks: all().map(function (el) {{
        var c = el.cloneNode(true);
        var t = c.querySelector('.ed-tools');
        if (t) t.remove();
        return {{ kind: el.dataset.kind, html: c.innerHTML }};
      }})
    }};
    fetch('/save', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(payload)
    }}).then(function (r) {{ return r.json(); }}).then(function (d) {{
      if (d.ok) {{
        dirty = false;
        status.textContent = 'Desat. ' + (d.note || '');
      }} else {{
        status.textContent = 'Error: ' + d.error;
        saveBtn.disabled = false;
      }}
    }}).catch(function (err) {{
      status.textContent = 'Error: ' + err;
      saveBtn.disabled = false;
    }});
  }}

  saveBtn.addEventListener('click', send);
  document.addEventListener('keydown', function (e) {{
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {{ e.preventDefault(); send(); }}
  }});
  window.addEventListener('beforeunload', function (e) {{
    if (dirty) {{ e.preventDefault(); e.returnValue = ''; }}
  }});
}})();
</script>
"""


def goto_options(current):
    """<optgroup> per RA (i el portal solt) amb referència i títol."""
    out = []
    all_pages = pages()

    def option(rel):
        ref, title, _, _ = page_summary(rel)
        sel = ' selected' if rel == current else ''
        label = html.escape(title if ref == 'Portal' else f'{ref} · {title}')
        return f'<option value="{html.escape(rel)}"{sel}>{label}</option>'

    if 'index.html' in all_pages:
        out.append(option('index.html'))
    for ra in ra_folders():
        ra_pages = [p for p in all_pages if ra_of(p) == ra.name]
        if not ra_pages:
            continue
        out.append(f'<optgroup label="{ra.name}">')
        out += [option(p) for p in ra_pages]
        out.append('</optgroup>')
    return '\n'.join(out)


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, body, ctype='text/html; charset=utf-8', code=200):
        raw = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == '/':
            return self.reply(render_index())

        if url.path == '/edit':
            rel = urllib.parse.parse_qs(url.query).get('f', [''])[0]
            try:
                src = resolve(rel).read_text(encoding='utf-8')
            except (ValueError, OSError) as e:
                return self.reply(f'<p>{e}</p>', code=404)
            bar = BAR.format(rel_json=json.dumps(rel), kinds_json=json.dumps(KINDS),
                             pages_json=json.dumps(pages()), options=goto_options(rel),
                             dense_json=json.dumps(sorted(revisa.DENSE)),
                             max_words=revisa.MAX_WORDS)
            return self.reply(src.replace('</body>', bar + '</body>'))

        self.reply('<p>No hi ha res aquí.</p>', code=404)

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != '/save':
            return self.reply('{"ok":false,"error":"ruta desconeguda"}',
                              'application/json', 404)
        n = int(self.headers.get('Content-Length', 0))
        try:
            data = json.loads(self.rfile.read(n))
            note = save(data['f'], data.get('header'), data['blocks'])
        except Exception as e:
            print(f'  error en desar: {e}')
            return self.reply(json.dumps({'ok': False, 'error': str(e)}),
                              'application/json')
        print(f'  desat {data["f"]}  ·  {note}')
        return self.reply(json.dumps({'ok': True, 'note': note}), 'application/json')


class Server(socketserver.TCPServer):
    # Permet reobrir el port just després d'aturar l'editor.
    allow_reuse_address = True


def start():
    """Arrenca al primer port lliure a partir de PORT."""
    for port in range(PORT, PORT + 10):
        try:
            return Server(('127.0.0.1', port), Handler), port
        except OSError:
            print(f'El port {port} està ocupat, provo el següent...')
    sys.exit(f'No hi ha cap port lliure entre {PORT} i {PORT + 9}.')


if __name__ == '__main__':
    srv, port = start()
    with srv:
        print(f'Editor a http://localhost:{port}   ({ROOT})')
        print('Atura\'l amb Ctrl+C.')
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print('\nAturat.')
