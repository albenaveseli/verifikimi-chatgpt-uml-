#!/usr/bin/env python3
"""
extract_logbooks.py – nxjerr nga logbook-ët e autorëve (LogBooks.zip në
github.com/atenearesearchgroup/chatgpt-uml) diagramet PlantUML që ChatGPT
gjeneroi në vitin 2023, për ushtrimet Video club, Airlines dhe Amphibious.
Gjithashtu numëron sesionet për çdo ushtrim (për krahasim me Tab. 2, f. 787).

Përdorimi:
  pip install pypdf
  python extract_logbooks.py LogBooks/        (dosja ku është çzipuar LogBooks.zip)

Rezultati: dosja logbook_2023/ me skedarë P<n>_<ushtrimi>_<k>.puml
"""
import os
import re
import sys

from pypdf import PdfReader

WANT = {'JT2': 'video', 'LB2': 'video', 'LB5': 'airlines', 'AV1': 'amphibious'}
ALL = {'AV1': 'Amphibious', 'AV8': 'Car parts', 'JC3': 'File system', 'JC6': 'Robots',
       'JT2': 'Video club', 'LB2': 'Video club', 'JT8': 'Theaters', 'LB4': 'Students', 'LB5': 'Airlines'}


def main(folder):
    os.makedirs('logbook_2023', exist_ok=True)
    sessions = {}
    for n in (1, 2, 3, 4):
        path = os.path.join(folder, f'Logbook-participant{n}.pdf')
        if not os.path.exists(path):
            print('mungon', path)
            continue
        text = '\n'.join(p.extract_text() or '' for p in PdfReader(path).pages)
        text = re.sub(r'Model:\s*\n\s*', 'Model: ', text)
        cur, buf, count = None, None, {}
        for raw in text.split('\n'):
            s = raw.strip()
            m = re.match(r'^(?:\d\)\s*)?Model:\s*([A-Z]{2}\d+)', s)
            if m:
                cur = m.group(1)
                sessions.setdefault(ALL.get(cur, cur), {})[n] = 0
                continue
            if cur is None:
                continue
            if re.match(r'^Session \d+$', s):
                sessions[ALL.get(cur, cur)][n] += 1
            if cur in WANT:
                if s.startswith('@startuml'):
                    buf = [s]
                elif buf is not None:
                    buf.append(s)
                    if s.startswith('@enduml'):
                        k = WANT[cur]
                        count[k] = count.get(k, 0) + 1
                        with open(f'logbook_2023/P{n}_{k}_{count[k]}.puml', 'w', encoding='utf-8') as fh:
                            fh.write('\n'.join(buf) + '\n')
                        buf = None
        print(f'Pjesëmarrësi {n}: diagrame të nxjerra {count}')
    print('\nSesionet sipas logbook-ëve (krahasoni me Tab. 2, f. 787):')
    for ex, d in sessions.items():
        vals = [d.get(n) for n in (1, 2, 3, 4)]
        nums = [v for v in vals if v]
        avg = sum(nums) / len(nums) if nums else 0
        print(f'  {ex:<12} P1–P4: {vals}  mesatarja: {avg:.2f}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'LogBooks')
