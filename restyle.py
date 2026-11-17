"""Apply the Avarthana corporate visual system to all website pages."""
from pathlib import Path
from html import escape as e
from urllib.parse import quote
import json, re

ROOT = Path(__file__).parent
D = ROOT / 'dist'
P = json.loads((ROOT / 'products.json').read_text(encoding='utf-8'))
AR = '<svg class="icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M6 18 18 6M6 6h12v12"/></svg>'
ARR = '<svg class="icon ribbon-arrow" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>'


def a(url, text):
    return f'<a href="{url}">{text} ↗</a>'


def mega(kind):
    if kind == 'applications':
        col1 = (
            '<div>'
            '<p class="eyebrow">OUR EXPERTISE</p>'
            '<a href="/capabilities/#radar">Advanced Radars &amp; RF Solutions ↗</a>'
            '<a href="/capabilities/#embedded">Embedded Engineering ↗</a>'
            '<a href="/capabilities/#aerospace">Aerospace &amp; Defence ↗</a>'
            '<a href="/capabilities/#hardware">Hardware Systems ↗</a>'
            '<a href="/capabilities/#software">Interactive Application Software ↗</a>'
            '</div>'
        )
        col2 = (
            '<div>'
            '<p class="eyebrow">SUPPORTING CAPABILITIES</p>'
            '<a href="/applications/#integration">System Design &amp; Integration ↗</a>'
            '<a href="/applications/#collaboration">Industrial &amp; Academic Collaboration ↗</a>'
            '<a href="/applications/#manufacturing">Manufacturing &amp; Testing Network ↗</a>'
            '<a href="/applications/#prototyping">Concept &amp; Prototype Development ↗</a>'
            '</div>'
        )
        return (
            '<div class="wrap mega-grid what-menu">'
            '<div><p class="eyebrow">WHAT WE DO</p>'
            '<h3>Engineering solutions across defence and aerospace.</h3>'
            '<p>From radar and embedded engineering to hardware systems and interactive application software.</p></div>'
            f'{col1}{col2}</div>'
        )

    if kind == 'products':
        cats = [
            ('RF &amp; Transceivers', 'RF & Transceivers'),
            ('Radar &amp; AI Processing', 'Radar & AI Processing'),
            ('Integrated Systems', 'Integrated Systems'),
            ('Radar Infrastructure', 'Radar Infrastructure'),
        ]
        col1 = (
            '<div>'
            '<p class="eyebrow">PRODUCT CATEGORIES</p>'
            + ''.join(f'<a href="/products/?category={quote(val, safe="")}#catalogue">{label} ↗</a>' for label, val in cats)
            + '</div>'
        )
        col2 = (
            '<div>'
            '<p class="eyebrow">FORM FACTORS</p>'
            '<a href="/products/?form=3U#catalogue">3U OpenVPX ↗</a>'
            '<a href="/products/?form=6U#catalogue">6U OpenVPX ↗</a>'
            '<a href="/products/?form=' + quote('Antenna backplane', safe='') + '#catalogue">Antenna Backplane ↗</a>'
            '<a href="/products/?category=' + quote('Integrated Systems', safe='') + '#catalogue">Line Replaceable Units ↗</a>'
            '</div>'
        )
        return (
            '<div class="wrap mega-grid product-menu">'
            '<div><p class="eyebrow">PRODUCTS</p>'
            '<h3>Platforms for the complete signal chain.</h3>'
            '<p>From RF acquisition and programmable processing to integrated systems, explore Avarthana hardware for defence and aerospace engineering.</p></div>'
            f'{col1}{col2}</div>'
        )

    if kind == 'company':
        return (
            '<div class="wrap mega-grid company-menu">'
            '<div><p class="eyebrow">COMPANY</p>'
            '<h3>Engineering solutions from Bengaluru, India.</h3>'
            '<p>An electronics engineering company connecting FPGA design, RF acquisition, embedded computing and radar processing.</p></div>'
            '<div><p class="eyebrow">AVARTHANA</p>'
            '<a href="/company/">Our company ↗</a>'
            '<a href="/capabilities/">Engineering expertise ↗</a>'
            '<a href="/applications/">What we do ↗</a></div>'
            '<div><p class="eyebrow">CONNECT</p>'
            '<a href="/contact/">Contact our engineers ↗</a>'
            '<a href="/resources/">Documentation &amp; downloads ↗</a></div>'
            '</div>'
        )

    return (
        '<div class="wrap mega-grid resources-menu">'
        '<div><p class="eyebrow">RESOURCES</p>'
        '<h3>Datasheets and engineering block diagrams.</h3>'
        '<p>Technical specifications, block diagrams and the consolidated portfolio catalogue to support your evaluation.</p></div>'
        '<div><p class="eyebrow">DOCUMENTATION</p>'
        '<a href="/resources/">Download centre ↗</a>'
        '<a href="/downloads/avarthana-product-catalogue.pdf" download>Complete product catalogue (PDF) ↗</a></div>'
        '<div><p class="eyebrow">ENGINEERING SUPPORT</p>'
        '<a href="/contact/">Discuss your requirements ↗</a>'
        '<a href="/products/">Browse product portfolio ↗</a></div>'
        '</div>'
    )


def header(old):
    brand = re.search(r'<a class="brand".*?</a>', old).group()
    mobile = re.search(r'<nav id="mobile-nav".*?</nav>', old).group()
    nav = ''
    for name, key, url in [
        ('What we do', 'applications', '/applications/'),
        ('Products', 'products', '/products/'),
        ('Company', 'company', '/company/'),
        ('Resources', 'resources', '/resources/'),
    ]:
        nav += (
            f'<div class="nav-item">'
            f'<a class="nav-trigger" href="{url}" aria-controls="mega-{key}" aria-expanded="false">{name}<span aria-hidden="true">⌄</span></a>'
            f'<div class="mega-menu" id="mega-{key}">{mega(key)}<div class="mega-bottom wrap">{a(url, "Explore " + name)}{a("/contact/", "Discuss your requirements")}</div></div>'
            f'</div>'
        )
    nav += '<a href="/capabilities/">Expertise</a>'
    return (
        f'<a class="skip-link" href="#main">Skip to content</a>'
        f'<header class="site-header"><div class="nav-wrap">{brand}'
        f'<nav class="desktop-nav" aria-label="Main navigation">{nav}</nav>'
        f'<div class="nav-actions">'
        f'<button class="search-open" aria-label="Search products"><svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg></button>'
        f'<a class="button small nav-contact" href="/contact/">CONTACT US</a>'
        f'<button class="menu-toggle" aria-label="Open navigation" aria-expanded="false" aria-controls="mobile-nav"><svg class="icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button>'
        f'</div></div>{mobile}</header>'
    )


def tile(p):
    return f'<a class="platform-tile" href="/products/{p["slug"]}/"><div class="tile-label"><span>{e(p["title"])}</span>{AR}</div><div class="hardware-orbit"><img src="{p["image"]}" alt="{e(p["title"])}" loading="lazy"></div><p>{e(p["subtitle"])}</p><span class="tile-foot">EXPLORE PLATFORM →</span></a>'


def homepage():
    slides = []
    for i, (bg, head, sub, p, label, url) in enumerate([
        ('defence', 'RF platforms.<br><em>Real possibilities.</em>', 'Multichannel acquisition and programmable processing. From the first signal to an integrated system.', P[0], 'EXPLORE RF PLATFORMS', '/products/?category=RF%20%26%20Transceivers'),
        ('space', 'Compact format.<br><em>Connected thinking.</em>', 'Discover 3U OpenVPX platforms built around RFSoC, Versal and Agilex technology.', P[5], 'EXPLORE 3U OPENVPX', '/products/?form=3U'),
        ('industrial', 'Beyond the board.<br><em>Into the system.</em>', 'RFSoC, Versal, timing and power. Explore our modular, cooled VPX line replaceable units.', P[12], 'EXPLORE INTEGRATED SYSTEMS', '/products/?category=Integrated%20Systems'),
    ]):
        slides.append(f'<section class="banner-slide {"is-active" if i==0 else ""}" data-slide="{i}" aria-hidden="{"false" if i==0 else "true"}" {"" if i==0 else "hidden"}><img class="banner-background" src="/assets/{bg}.webp" alt="" {"fetchpriority=high" if i==0 else "loading=lazy"}><div class="wrap banner-content"><div class="banner-copy"><p class="eyebrow">AVARTHANA / RF • FPGA • OPENVPX</p><{"h1" if i==0 else "h2"}>{head}</{"h1" if i==0 else "h2"}><p>{sub}</p><a class="button button-cyan" href="{url}">{label}</a></div><a class="banner-hardware" href="/products/{p["slug"]}/" aria-label="Explore {e(p["title"])}"><div class="hardware-orbit"><img src="{p["image"]}" alt="{e(p["title"])} product render"></div><span>{e(p["title"])} {AR}</span></a></div></section>')
    hero = '<section class="epiq-banner" aria-roledescription="carousel" aria-label="Featured Avarthana platforms">' + ''.join(slides) + '<button class="banner-prev" aria-label="Previous featured platform">‹</button><button class="banner-next" aria-label="Next featured platform">›</button><div class="banner-controls"><div class="banner-dots">' + ''.join(f'<button aria-label="Show featured platform {i+1}" aria-pressed="{"true" if i==0 else "false"}" data-slide-to="{i}"></button>' for i in range(3)) + '</div><button class="banner-pause" aria-label="Pause slideshow">Ⅱ</button></div></section>'
    intro = '<section class="section platform-intro"><div class="wrap"><div class="portfolio-introduction"><h2>RF. Compute.<br>Integration.</h2><div><h3>Engineering the complete signal chain.</h3><p>Acquisition, programmable processing and system integration belong in the same conversation. Avarthana connects them through a portfolio of RFSoC, Versal, Agilex and NVIDIA Jetson platforms, OpenVPX cards and integrated systems.</p><a class="button button-cyan" href="/products/">EXPLORE ALL PRODUCTS</a></div></div><div class="platform-family-grid">' + ''.join(f'<a class="family-tile" href="{url}"><span>{title} {AR}</span><div class="hardware-orbit"><img src="{P[idx]["image"]}" alt="{e(title)}" loading="lazy"></div><p>{sub}</p></a>' for title, url, idx, sub in [('3U OpenVPX', '/products/?form=3U', 5, 'Compact RF & radar processing'), ('6U OpenVPX', '/products/?form=6U', 0, 'Multichannel RF & digital processing'), ('Integrated systems', '/products/?category=Integrated%20Systems', 12, 'Air & liquid-cooled LRUs'), ('Radar infrastructure', '/products/?category=Radar%20Infrastructure', 14, 'Array mounting & support')]) + '</div></div></section>'
    featured = '<section class="section featured-platforms"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">THE HARDWARE BEHIND YOUR NEXT DESIGN</p><h2>Explore our platforms.</h2></div>' + a('/products/', f'View all {len(P)} products') + '</div><div class="featured-grid">' + ''.join(tile(P[i]) for i in [1, 8, 11]) + '</div></div></section>'
    apps = '<section class="section epiq-applications"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">APPLICATIONS & PLATFORMS</p><h2>Where the technology<br>meets the challenge.</h2></div><div><p>Explore electronics and processing platforms for defence, aerospace, industry and research.</p><a class="button button-dark" href="/applications/">EXPLORE APPLICATIONS</a></div></div><div class="application-grid">' + ''.join(f'<a class="application-card" href="/applications/#{slug}"><img src="/assets/{slug}.webp" alt="{title} application illustration" loading="lazy"><div><p class="eyebrow">AVARTHANA APPLICATIONS</p><h3>{title}</h3>{AR}</div></a>' for slug, title in [('defence', 'Defence & radar'), ('aerospace', 'Aerospace'), ('industrial', 'Industrial & research')]) + '</div></div></section>'
    system = f'<section class="section epiq-system"><div class="wrap"><div class="portfolio-introduction"><div><p class="eyebrow">BUILD THE BIGGER PICTURE</p><h2>From a card.<br>To a complete system.</h2><p>Combine eight RFSoC cards, two Versal cards, clock distribution and power in an integrated 6U VPX architecture. Explore liquid-cooled and forced-air-cooled configurations.</p><a class="button button-cyan" href="/products/6u-liquid-cooled-lru/">DISCOVER OUR LRUs</a></div><div class="hardware-orbit"><img src="{P[12]["image"]}" alt="6U liquid-cooled LRU" loading="lazy"></div></div></div></section>'
    resources = '<section class="section epiq-resources"><div class="wrap"><div class="section-heading"><h2>Technical resources.</h2>' + a('/resources/', 'All downloads') + '</div><div class="featured-grid">' + ''.join(f'<a class="technical-card" href="{p["datasheet"]}" download><div class="resource-render"><img src="{p["image"]}" alt="" loading="lazy"></div><p class="eyebrow">PRODUCT BROCHURE / PDF</p><h3>{e(p["title"])}</h3><p>{e(p["subtitle"])}</p><span>DOWNLOAD BROCHURE {AR}</span></a>' for p in [P[0], P[5], P[12]]) + '</div></div></section>'
    return hero + intro + featured + apps + system + resources


def apply():
    for path in D.rglob('*.html'):
        if path.name.startswith('__'):
            continue
        text = path.read_text(encoding='utf-8')
        old = re.search(r'<a class="skip-link".*?</header>', text, re.S)
        if old:
            text = text[:old.start()] + header(old.group()) + text[old.end():]
        text = text.replace('<link rel="stylesheet" href="/assets/style.css">', '<link rel="stylesheet" href="/assets/style.css"><link rel="stylesheet" href="/assets/avarthana.css">')
        text = text.replace('<script src="/assets/app.js" defer></script>', '<script src="/assets/app.js" defer></script><script src="/assets/site-interactions.js" defer></script>')
        text = re.sub(r'(<div class="detail-image"><span class="detail-cross">\+</span>)(<img[^>]+>)', r'\1<div class="hardware-orbit">\2</div>', text)
        if path == D / 'index.html':
            oldmain = re.search(r'<main id="main">(.*?)</main>', text, re.S)
            cta = re.search(r'<section class="contact-band".*', oldmain.group(1), re.S).group()
            text = text[:oldmain.start()] + '<main id="main">' + homepage() + cta + '</main>' + text[oldmain.end():]
        path.write_text(text, encoding='utf-8')
    print('Applied Avarthana corporate design to all website pages')


if __name__ == '__main__':
    apply()
