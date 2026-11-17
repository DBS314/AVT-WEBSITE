"""Photography, download-centred product pages, and a restrained premium interface."""
from pathlib import Path
from html import escape as e
import json, re

ROOT = Path(__file__).parent
D = ROOT / 'dist'
P = json.loads((ROOT / 'products.json').read_text(encoding='utf-8'))
AR = '<svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/></svg>'


def size(n):
    return f'{n/1024/1024:.1f} MB' if n >= 1024 * 1024 else f'{max(1, round(n/1024))} KB'


def doc_link(p, key, label, kind):
    pages = p.get('document_pages', {}).get(key, 2 if kind == 'datasheet' else 1)
    return (
        f'<a class="document-button" href="{p[key]}" download data-doc-type="{kind}" '
        f'aria-label="Download {e(label)} for {e(p["title"]+" "+p["subtitle"])}">'
        f'<span class="document-format">PDF</span>'
        f'<span><strong>{label}</strong><small>{size(p["document_sizes"][key])} · {pages} {"page" if pages == 1 else "pages"}</small></span>'
        f'{AR}</a>'
    )


def docs(p):
    links = doc_link(p, 'datasheet', 'Datasheet', 'datasheet')
    if p.get('diagram_pdf'):
        links += doc_link(p, 'diagram_pdf', 'Block diagram', 'diagram')
    else:
        links += (
            f'<div class="document-unavailable"><span class="document-format">PDF</span>'
            f'<span><strong>Block diagram</strong><small>Available on request from engineering.</small>'
            f'<a href="/contact/?product={p["slug"]}">Request diagram ↗</a></span></div>'
        )
    return '<div class="document-buttons">' + links + '</div>'


def downloads_section(p):
    return (
        f'<section class="product-section document-section" id="downloads">'
        f'<p class="eyebrow">PRODUCT DOCUMENTATION</p>'
        f'<h2>Product documentation.</h2>'
        f'<p class="document-intro">Download the product datasheet and block diagram as separate PDF files.</p>'
        f'{docs(p)}</section>'
    )


def resources():
    cats = ['RF & Transceivers', 'Radar & AI Processing', 'Integrated Systems', 'Radar Infrastructure']
    cards = []
    for p in P:
        search = e(' '.join([p['title'], p['subtitle'], p['processor'], p['category'], p['family']]).lower())
        cards.append(
            f'<article class="resource-item download-product" data-search="{search}" data-category="{e(p["category"])}" data-has-diagram="{str(bool(p.get("diagram_pdf"))).lower()}">'
            f'<div class="download-product-heading">'
            f'<a class="download-product-visual" href="/products/{p["slug"]}/"><img src="{p["image"]}" alt="{e(p["title"])}" loading="lazy"></a>'
            f'<div><p class="eyebrow">{e(p["category"])}</p><h2><a href="/products/{p["slug"]}/">{e(p["title"])}</a></h2><p>{e(p["subtitle"])}</p></div>'
            f'<a class="download-product-page" href="/products/{p["slug"]}/" aria-label="View {e(p["title"]+" "+p["subtitle"])}">View product ↗</a>'
            f'</div>{docs(p)}</article>'
        )
    cat_path = D / 'downloads/avarthana-product-catalogue.pdf'
    cat_size = size(cat_path.stat().st_size) if cat_path.exists() else '10.3 MB'
    cat_pages = sum(p.get('document_pages', {}).get('datasheet', 2) for p in P)
    return (
        f'<section class="download-centre-hero"><div class="wrap">'
        f'<p class="breadcrumb"><a href="/">Home</a> / Resources</p>'
        f'<p class="eyebrow">AVARTHANA DOWNLOAD CENTRE</p>'
        f'<h1>Every detail.<br><span>One place.</span></h1>'
        f'<p>Find and download the datasheet and block diagram for your platform.</p>'
        f'<div class="document-totals"><span>{len(P)} product datasheets</span><span>{sum(bool(x.get("diagram_pdf")) for x in P)} block diagrams</span><span>Consolidated PDF catalogue</span></div>'
        f'</div></section>'
        f'<section class="section downloads-section"><div class="wrap">'
        f'<div class="download-filters">'
        f'<label class="catalogue-search"><svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><input id="resource-search" type="search" placeholder="Search product, platform or form factor" aria-label="Find a product document"></label>'
        f'<label><span class="sr-only">Product family</span><select id="resource-family"><option value="">All product families</option>{"".join(f"<option>{e(c)}</option>" for c in cats)}</select></label>'
        f'<label><span class="sr-only">Document type</span><select id="resource-type"><option value="all">All documents</option><option value="datasheet">Datasheets</option><option value="diagram">Block diagrams</option></select></label>'
        f'</div>'
        f'<div class="download-result-bar"><p id="document-result-count" role="status">{len(P)} products</p><button type="button" class="text-button" id="reset-document-filters">Reset filters</button></div>'
        f'<div class="download-products">{"".join(cards)}</div>'
        f'<p id="resource-empty" hidden>No matching documentation. Try another platform or clear the filters.</p>'
        f'<div class="complete-catalogue"><div><p class="eyebrow">THE FULL PICTURE</p><h2>The complete catalogue.</h2>'
        f'<p>Explore all {len(P)} Avarthana datasheets in one consolidated PDF ({cat_size} · {cat_pages} pages).</p></div>'
        f'<a class="button button-cyan" href="/downloads/avarthana-product-catalogue.pdf" download>Download catalogue {AR}</a></div>'
        f'</div></section>'
    )


def apply():
    image_map = {
        '/assets/defence.webp': '/assets/original/radar.webp',
        '/assets/aerospace.webp': '/assets/original/mechanical.webp',
        '/assets/industrial.webp': '/assets/original/electronics.webp',
        '/assets/space.webp': '/assets/original/rf.webp',
        '/assets/about-engineering.webp': '/assets/original/electronics.webp',
    }
    for path in D.rglob('*.html'):
        if path.name.startswith('__'):
            continue
        s = path.read_text(encoding='utf-8')
        if path == D / 'index.html':
            s = re.sub(r'<section class="section epiq-resources">.*?</section>', '', s, flags=re.S)
            s = s.replace('application illustration', 'application photograph')
        if path.parent.parent == D / 'products' and path.name == 'index.html':
            p = next(x for x in P if x['slug'] == path.parent.name)
            s = re.sub(r'<section class="product-section" id="architecture">.*?</section>', '', s, flags=re.S)
            s = re.sub(r'<section class="product-section" id="downloads">.*?</section>', downloads_section(p), s, flags=re.S)
            s = re.sub(r'<a href="#architecture">.*?</a>', '', s)
            s = s.replace('Download brochure', 'Download datasheet')
            s = s.replace('<a href="#downloads">Downloads</a>', '<a href="#downloads">Documentation</a>')
        if path == D / 'resources/index.html':
            s = re.sub(r'<main id="main">.*?</main>', '<main id="main">' + resources() + '</main>', s, flags=re.S)
        s = re.sub(r'<div class="announcement">.*?</div>', '', s, flags=re.S)
        s = s.replace('<link rel="stylesheet" href="/assets/avarthana.css">', '<link rel="stylesheet" href="/assets/avarthana.css"><link rel="stylesheet" href="/assets/refined.css">')
        s = s.replace('<script src="/assets/site-interactions.js" defer></script>', '<script src="/assets/site-interactions.js" defer></script><script src="/assets/refined.js" defer></script>')
        for old, new in image_map.items():
            s = s.replace(old, new)
        s = s.replace('application illustration', 'application photograph').replace('Avarthana electronics engineering illustration', 'Electronics research laboratory photograph')
        path.write_text(s, encoding='utf-8')
    print('Refined all pages: real photographs, downloadable documentation and premium interactions')
