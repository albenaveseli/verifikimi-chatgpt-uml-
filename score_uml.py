#!/usr/bin/env python3
"""
score_uml.py – krahason një diagram klasash PlantUML të gjeneruar nga një LLM
me modelin synim (target model) dhe llogarit precision / recall / F1 për çdo
kategori elementesh, si në Chen et al. (2023).

Përdorimi:
  python score_uml.py targets/airlines.puml outputs/airlines_run1.puml
  python score_uml.py targets/airlines.puml outputs/airlines_*.puml --csv rezultatet.csv
  python score_uml.py targets/video.puml outputs/video_run1.puml --alias Customer=Client --alias VideoClub=VideoStore

Kategoritë:
  classes      – klasat (përfshirë abstraktet)
  abstract_classes – cilat klasa janë abstrakte
  enums        – numërimet (enumerations)
  attributes   – (klasa, atributi)
  operations   – (klasa, operacioni)
  associations – çiftet e klasave të lidhura (asociacion, agregim ose kompozim)
  generalizations – (nënklasa, superklasa); „realization” (<|..) NUK numërohet si trashëgimi
  assoc_classes   – (çifti i klasave, klasa e asociacionit)
Plus: multiplicities – sa nga asociacionet e gjetura kanë shumëfishësitë e sakta.

Kufizime: krahasimi bëhet sipas emrave (pa dallim shkronjash të mëdha/vogla,
njëjës/shumës), prandaj prompt-i duhet t'i japë emrat e klasave, ose përdoret --alias.
Kufizimet OCL nuk vlerësohen.
"""
import argparse
import csv
import glob
import re
import sys

ARROW = r'[<|o*x#}+.\-]*[-.]{2,}[>|o*x#{+]*'
REL_RE = re.compile(
    r'^\s*"?([\w]+)"?\s*(?:"([^"]*)")?\s*(' + ARROW + r'|[<|o*]*-[-]?[>|o*]*|-[a-z]*-)\s*(?:"([^"]*)")?\s*"?([\w]+)"?\s*(?::\s*(.*))?$')
ACLASS_RE = re.compile(r'^\s*\(\s*"?(\w+)"?\s*,\s*"?(\w+)"?\s*\)\s*\.\.+\s*"?(\w+)"?')
CLASS_RE = re.compile(r'^\s*(abstract\s+class|abstract|class|interface|enum|entity)\s+"?([\w]+)"?(?:\s+as\s+(\w+))?[^{]*?(\{)?\s*$', re.I)


def norm(name, alias):
    n = re.sub(r'[^a-z0-9]', '', name.lower())
    n = alias.get(n, n)
    if len(n) > 3 and n.endswith('s') and not n.endswith('ss'):
        n = n[:-1]
    return n


def norm_mult(m):
    if m is None:
        return None
    m = m.replace(' ', '')
    return {'*': '0..*', 'n': '0..*', '0..n': '0..*', '1..n': '1..*', '': None}.get(m, m)


def parse(path, alias):
    text = open(path, encoding='utf-8', errors='replace').read()
    m = re.search(r'@startuml(.*?)@enduml', text, re.S)
    body = m.group(1) if m else text
    lines = [l.split("'")[0].rstrip() if not l.strip().startswith("'") else '' for l in body.split('\n')]
    model = {k: set() for k in ('classes', 'abstract_classes', 'enums', 'attributes', 'operations',
                                'associations', 'generalizations', 'assoc_classes', 'realizations')}
    mult = {}
    cur, cur_kind = None, None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if cur is not None:
            if line.startswith('}'):
                cur = None
                continue
            member = re.sub(r'^[-+#~]\s*', '', line)
            member = re.sub(r'\{(static|abstract)\}\s*', '', member)
            if cur_kind == 'enum':
                for lit in re.split(r'[,\s]+', member):
                    if lit:
                        model['attributes'].add((cur, 'literal:' + norm(lit, alias)))
                continue
            if '(' in member:
                name = re.match(r'(?:[\w<>\[\]]+\s+)?(\w+)\s*\(', member)
                if name:
                    model['operations'].add((cur, norm(name.group(1), alias)))
            else:
                if ':' in member:
                    name = member.split(':')[0].strip().split()[-1] if member.split(':')[0].strip() else ''
                else:
                    parts = member.split()
                    name = parts[-1] if parts else ''
                if name and re.match(r'^\w+$', name):
                    model['attributes'].add((cur, norm(name, alias)))
            continue
        mc = CLASS_RE.match(line)
        if mc and not REL_RE.match(line):
            kind = mc.group(1).lower()
            name = norm(mc.group(3) or mc.group(2), alias)
            if kind == 'enum':
                model['enums'].add(name)
            else:
                model['classes'].add(name)
                if kind.startswith('abstract') or '<<abstract>>' in line.lower():
                    model['abstract_classes'].add(name)
            if mc.group(4):
                cur, cur_kind = name, ('enum' if kind == 'enum' else 'class')
            continue
        ma = ACLASS_RE.match(line)
        if ma:
            a, b, c = (norm(x, alias) for x in ma.groups())
            model['assoc_classes'].add((frozenset((a, b)), c))
            continue
        mr = REL_RE.match(line)
        if mr:
            a, ma_, arrow, mb_, b, _label = mr.groups()
            a, b = norm(a, alias), norm(b, alias)
            if a == b and arrow.count('-') + arrow.count('.') < 2:
                continue
            if '|' in arrow and ('<|' in arrow or '|>' in arrow):
                if '<|' in arrow:
                    child, parent = b, a
                else:
                    child, parent = a, b
                if '..' in arrow:
                    model['realizations'].add((child, parent))
                else:
                    model['generalizations'].add((child, parent))
            elif '..' in arrow and not any(ch in arrow for ch in 'o*'):
                continue  # dependency / note link
            else:
                pair = frozenset((a, b))
                model['associations'].add(pair)
                mult[pair] = {a: norm_mult(ma_), b: norm_mult(mb_)}
    # klasat e përmendura vetëm në marrëdhënie
    for pair in model['associations']:
        model['classes'] |= set(pair) - model['enums']
    for c, p in model['generalizations'] | model['realizations']:
        model['classes'] |= {c, p} - model['enums']
    for pair, c in model['assoc_classes']:
        model['classes'] |= set(pair) | {c}
    # numërimet nuk janë klasa
    model['classes'] -= model['enums']
    return model, mult


def prf(t, o):
    tp = len(t & o)
    fp = len(o - t)
    fn = len(t - o)
    p = tp / (tp + fp) if tp + fp else (1.0 if not t else 0.0)
    r = tp / (tp + fn) if tp + fn else 1.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return tp, fp, fn, p, r, f


CATS = ['classes', 'abstract_classes', 'enums', 'attributes', 'operations', 'associations', 'generalizations', 'assoc_classes']


def score(target_path, out_path, alias):
    t, tm = parse(target_path, alias)
    o, om = parse(out_path, alias)
    res = {}
    tot = [0, 0, 0]
    for c in CATS:
        if not t[c] and not o[c]:
            continue
        tp, fp, fn, p, r, f = prf(t[c], o[c])
        res[c] = (tp, fp, fn, p, r, f)
        tot[0] += tp; tot[1] += fp; tot[2] += fn
    matched = t['associations'] & o['associations']
    ok = sum(1 for pair in matched if tm.get(pair) == om.get(pair))
    res['multiplicities'] = (ok, len(matched))
    P = tot[0] / (tot[0] + tot[1]) if tot[0] + tot[1] else 0
    R = tot[0] / (tot[0] + tot[2]) if tot[0] + tot[2] else 0
    res['TOTAL'] = (tot[0], tot[1], tot[2], P, R, 2 * P * R / (P + R) if P + R else 0)
    res['exact'] = all(v[1] == 0 and v[2] == 0 for k, v in res.items() if k in CATS) and ok == len(matched)
    res['realizations_as_inheritance'] = len(o['realizations'])
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target')
    ap.add_argument('outputs', nargs='+')
    ap.add_argument('--alias', action='append', default=[], help='EmriNeOutput=EmriNeTarget')
    ap.add_argument('--csv')
    a = ap.parse_args()
    alias = {}
    for s in a.alias:
        k, v = s.split('=')
        alias[re.sub(r'[^a-z0-9]', '', k.lower())] = re.sub(r'[^a-z0-9]', '', v.lower())
    files = []
    for pat in a.outputs:
        files += sorted(glob.glob(pat)) or [pat]
    rows = []
    for f in files:
        r = score(a.target, f, alias)
        print(f'\n=== {f}')
        print(f'{"kategoria":<17}{"TP":>4}{"FP":>4}{"FN":>4}{"P":>7}{"R":>7}{"F1":>7}')
        for c in CATS + ['TOTAL']:
            if c in r:
                tp, fp, fn, p, rr, f1 = r[c]
                print(f'{c:<17}{tp:>4}{fp:>4}{fn:>4}{p:>7.2f}{rr:>7.2f}{f1:>7.2f}')
        ok, n = r['multiplicities']
        print(f'shumëfishësi të sakta: {ok}/{n}')
        if r['realizations_as_inheritance']:
            print(f'KUJDES: {r["realizations_as_inheritance"]} „realization” (<|..) në vend të trashëgimisë')
        print('PËRPUTHJE E PLOTË me modelin synim:', 'PO' if r['exact'] else 'JO')
        row = {'file': f, 'exact': r['exact'], 'mult_ok': f'{ok}/{n}'}
        for c in CATS + ['TOTAL']:
            if c in r:
                row[c + '_F1'] = round(r[c][5], 2)
        rows.append(row)
    if a.csv:
        keys = sorted({k for row in rows for k in row}, key=lambda k: (k != 'file', k))
        with open(a.csv, 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
        print(f'\nCSV: {a.csv}')


if __name__ == '__main__':
    main()
