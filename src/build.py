#!/usr/bin/env python3
"""Build single-file prototypes: paste the Lune UI head block where <!-- LUNE-UI-CSS --> sits.
Usage: python3 src/build.py            (builds every src/*.src.html into ./<name>.html)"""
import glob, json, os, subprocess
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo = open(os.path.expanduser('~/.claude/skills/lune-ui/assets/lune-logo.svg')).read().replace('<svg ', '<svg role="img" aria-label="Lune" ', 1)
block = subprocess.run(['python3', os.path.expanduser('~/.claude/skills/lune-ui/scripts/style_block.py')], capture_output=True, text=True, check=True).stdout
reqs = json.load(open(os.path.join(root, 'src', '_shared', 'rfp-reqs.effective.json')))
tips = open(os.path.join(root, 'src', '_shared', 'req-tips.js')).read()
import re
IDRE = re.compile(r'(CL|OM|MS|RC|LAF|LIT|LVP)-\d+(?:\.\d+)?|\d+(?:\.\d+)?|\bto\b')
def used_ids(text):
    # mirror of parse() in req-tips.js: explicit IDs, shorthand numbers after an ID, and 'X to Y' ranges
    out, prefix, major, dotted, last, rng = set(), None, None, False, None, False
    for m in IDRE.finditer(text):
        t = m.group(0)
        if t == 'to':
            rng = last is not None; continue
        mm = re.match(r'(CL|OM|MS|RC|LAF|LIT|LVP)-(\d+)(?:\.(\d+))?$', t)
        if mm:
            prefix, major, dotted = mm.group(1), mm.group(2), bool(mm.group(3)); i = t
        elif prefix:
            if dotted: i = prefix + '-' + (t if '.' in t else major + '.' + t)
            elif '.' not in t: i = prefix + '-' + t
            else: continue
        else: continue
        if rng and last:
            a = re.match(r'(\w+)-(\d+)(?:\.(\d+))?', last); c = re.match(r'(\w+)-(\d+)(?:\.(\d+))?', i)
            if a and c and a.group(1) == c.group(1):
                if a.group(3) and c.group(3) and a.group(2) == c.group(2) and int(c.group(3)) - int(a.group(3)) < 500:
                    out.update(f'{a.group(1)}-{a.group(2)}.{k}' for k in range(int(a.group(3)), int(c.group(3))))
                elif not a.group(3) and not c.group(3) and int(c.group(2)) - int(a.group(2)) < 500:
                    out.update(f'{a.group(1)}-{k}' for k in range(int(a.group(2)), int(c.group(2))))
            rng = False
        out.add(i); last = i
    return out
proto = open(os.path.join(root, 'src', '_shared', 'lune-proto.css')).read()
# Real partner data pulled from the RFP sheets (rfp-work/partner-data/*.json).
partner = {os.path.basename(f)[:-5]: json.load(open(f)) for f in sorted(glob.glob(os.path.join(root, 'rfp-work', 'partner-data', '*.json')))}
partner_js = json.dumps(partner, ensure_ascii=False).replace('</', '<\\/')
partner_model = open(os.path.join(root, 'src', '_shared', 'partner-model.js')).read()
for src in glob.glob(os.path.join(root, 'src', '*.src.html')):
    out = os.path.join(root, os.path.basename(src).replace('.src.html', '.html'))
    s = open(src).read()
    assert '<!-- LUNE-UI-CSS -->' in s, src
    s = s.replace('<!-- LUNE-UI-CSS -->', block).replace('<!-- LUNE-PROTO-CSS -->', '<style>' + proto + '</style>').replace("/*LUNE-LOGO*/''", json.dumps(logo)).replace('<!-- LUNE-LOGO -->', logo)
    if '<!-- RFP-TIPS -->' in s:
        ids = sorted(k for k in used_ids(s) if k in reqs)
        sub = {k: reqs[k] for k in ids}
        s = s.replace('<!-- RFP-TIPS -->', '<script>window.RFP_REQS=' + json.dumps(sub, ensure_ascii=False).replace('</', '<\\/') + ';</script><script>' + tips + '</script>')
    if os.path.basename(src) == 'pulse-admin.src.html':
        import sys as _s; _s.path.insert(0, os.path.join(root, 'src', '_shared')); import rebrand  # demo merchants -> RFP offer set (13 Nov 2026)
        s = rebrand.apply(s, 'admin')
    # Real partner data goes in after the rebrand, so the real brand names are never swapped.
    s = s.replace('/*PARTNER-MODEL*/', partner_model).replace('/*PARTNER-DATA*/{}', partner_js)
    open(out, 'w').write(s)
    print('built', os.path.basename(out), os.path.getsize(out))
