#!/usr/bin/env python3
"""Embed measured results into the self-contained static demo; no synthetic UI metrics."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/'projects/reliability-lab'
DATA=LAB/'results/reference'

def main():
    results=[json.loads((DATA/f'{profile}-0-{policy}.json').read_text(encoding='utf-8'))
             for profile in ('clean','transient','mixed','ack_loss','permanent','slow')
             for policy in ('baseline','retry','resilient','no_timeout')]
    recovery=json.loads((DATA/'recovery.json').read_text(encoding='utf-8'))
    payload={'results':results,'recovery':{k:recovery[k]['summary'] for k in ('pause','resumed','warm')}}
    encoded=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    path=LAB/'demo.html'
    content=path.read_text(encoding='utf-8')
    updated,count=re.subn(r'(<script id="reference-data" type="application/json">).*?(</script>)',
                         lambda match:match[1]+encoded+match[2],content,flags=re.S)
    if count != 1:
        raise RuntimeError('expected exactly one reference-data block')
    path.write_text(updated,encoding='utf-8')
    print(f'Embedded {len(results)} real local runs; {len(encoded)} JSON characters')

if __name__ == '__main__': main()
