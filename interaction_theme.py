from pathlib import Path
import re

D = Path(__file__).parent / 'dist'


def apply():
    for f in D.rglob('*.html'):
        if f.name.startswith('__'):
            continue
        s = f.read_text(encoding='utf-8').replace(
            '<link rel="stylesheet" href="/assets/cohesion.css">',
            '<link rel="stylesheet" href="/assets/cohesion.css"><link rel="stylesheet" href="/assets/interaction-theme.css">'
        )

        def classify(m):
            tag = m[0]
            if 'download' in tag and 'class="text-link"' in tag:
                tag = tag.replace('class="text-link"', 'class="text-link action-secondary"')
            return tag

        s = re.sub(r'<a\b[^>]*>', classify, s)

        rel_root = '../' * (len(f.relative_to(D).parts) - 1)

        def rel_attr(m):
            attr, rest = m.group(1), m.group(2)
            if rest.startswith('/'):
                return m.group(0)
            if rest == '':
                return f'{attr}="{rel_root or "./"}"'
            return f'{attr}="{rel_root}{rest}"'

        s = re.sub(r'\b(href|src)="/([^"]*)"', rel_attr, s)
        f.write_text(s, encoding='utf-8')
    (D / '.nojekyll').write_text('', encoding='utf-8')
    print('Applied differentiated primary, secondary, link, download and selection controls')
