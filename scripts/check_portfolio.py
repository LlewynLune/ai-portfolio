#!/usr/bin/env python3
"""Read-only structural checks; not a confidentiality or credential audit."""
from pathlib import Path
from html.parser import HTMLParser
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ['README.md', 'PUBLISHING.md', 'index.html', '.gitignore',
            'docs/portfolio-case-matrix.md', 'docs/github-setup-guide.md',
            'profile/README-template.md',
            'examples/evidence-trace/README.md',
            'examples/evidence-trace/evidence_trace.py',
            'examples/evidence-trace/sample-events.jsonl',
            'projects/product-workflow/README.md',
            'projects/research-evaluation/README.md',
            'projects/infra-runtime/README.md',
            'projects/reliability-lab/README.md',
            'projects/reliability-lab/demo.html',
            'projects/reliability-lab/ARCHITECTURE.md',
            'projects/reliability-lab/CONTRIBUTIONS.md',
            'projects/reliability-lab/results/reference/benchmark.json',
            'projects/reliability-lab/results/reference/REPORT.md',
            'projects/reliability-lab/results/advanced/REPORT.md',
            'projects/reliability-lab/results/advanced/advanced.json']

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.filters = set()
        self.tracks = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.add(a['id'])
        if tag == 'a' and 'href' in a:
            self.links.append(a['href'])
        if 'data-filter' in a:
            self.filters.add(a['data-filter'])
        if 'data-track' in a:
            self.tracks.add(a['data-track'])

def check(root=ROOT):
    errors = []
    for name in REQUIRED:
        if not (root / name).is_file():
            errors.append('Missing: ' + name)
    if errors:
        return errors
    html = (root / 'index.html').read_text(encoding='utf-8')
    page = PageParser()
    page.feed(html)
    for link in page.links:
        if link.startswith('#'):
            if link[1:] not in page.ids:
                errors.append('Missing section: ' + link)
        elif '://' not in link and not link.startswith('mailto:'):
            if not (root / link).is_file():
                errors.append('Missing HTML link: ' + link)
    if page.filters != {'all', 'product', 'research', 'infra'}:
        errors.append('Incorrect filters')
    if page.tracks != {'product', 'research', 'infra'}:
        errors.append('Incorrect project tracks')
    for path in root.rglob('*'):
        if any(part in {'.git', '.venv', 'private', '__pycache__'} for part in path.parts) or not path.is_file():
            continue
        if path.suffix not in {'.md', '.html'}:
            continue
        text = path.read_text(encoding='utf-8')
        if re.search(r'https?://[^\s"<>]*(?:larkoffice\.com|feishu\.cn|feishu\.doubao\.com|bytedance\.net)', text):
            errors.append('Internal link found: ' + str(path.relative_to(root)))
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if '://' not in link and not link.startswith('#'):
                    if not (path.parent / link).is_file():
                        errors.append('Missing Markdown link: ' + link)
    for name in REQUIRED:
        if name in {'projects/product-workflow/README.md', 'projects/research-evaluation/README.md', 'projects/infra-runtime/README.md'} and '状态：待填' not in (root / name).read_text(encoding='utf-8'):
            errors.append('Missing draft status: ' + name)
    return errors

if __name__ == '__main__':
    errors = check()
    for error in errors:
        print('ERROR:', error)
    if not errors:
        print('PASS: required files, local links, section targets, filters and draft labels')
        print('NOTE: no confidential-content audit performed; no project claims verified')
    sys.exit(bool(errors))
