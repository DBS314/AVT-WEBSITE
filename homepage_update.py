from pathlib import Path
from urllib.parse import quote
import re

D = Path(__file__).parent / 'dist'
AR = '↗'
CHECK = '<svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg>'

areas = [
    (
        'radar',
        'Advanced Radars & RF Solutions',
        'Clarity begins<br>with the signal.',
        'Radar and RF engineering, from signal acquisition and timing to real-time processing.',
        'We architect multichannel RF front ends, phased-array antenna backplanes and real-time radar signal chains built around AMD RFSoC, Versal and Agilex platforms.',
        [
            'Multichannel RF acquisition & waveform generation',
            'Digital beamforming, DDC/DUC & pulse compression',
            'Doppler filtering & CFAR target detection',
            'Phase-coherent synchronization & timing distribution',
        ],
        '/capabilities/#radar',
        '/products/?category=RF%20%26%20Transceivers#catalogue',
        'Explore radar & RF solutions',
        'rf',
    ),
    (
        'embedded',
        'Embedded Engineering',
        'Intelligence.<br>Engineered in.',
        'FPGA, embedded firmware and software working together across the signal chain.',
        'Programmable logic, embedded Arm/x86 computing and deterministic firmware unite to execute low-latency signal pipelines, data routing and autonomous system control.',
        [
            'VHDL / Verilog RTL design & timing closure',
            'High-speed optical & PCIe/Ethernet fabric integration',
            'Embedded Linux, RTOS & board support packages',
            'Hardware-in-the-loop simulation & verification',
        ],
        '/capabilities/#embedded',
        '/products/?category=Radar%20%26%20AI%20Processing#catalogue',
        'Explore embedded engineering',
        'electronics',
    ),
    (
        'aerospace',
        'Aerospace & Defence',
        'Engineering for<br>demanding environments.',
        'Connecting electronics, mechanical design and software for aerospace and defence applications.',
        'From ruggedized 3U and 6U OpenVPX cards to conduction- and liquid-cooled LRUs, our platforms are structured around VITA standards and MIL-STD qualification targets.',
        [
            'VITA 46 / VITA 65 OpenVPX & VITA 48 cooling',
            'Conduction-cooled & liquid-cooled LRU integration',
            'MIL-STD-810H & MIL-STD-461G design targets',
            'Built-in-test, health telemetry & fault reporting',
        ],
        '/capabilities/#aerospace',
        '/products/?category=Integrated%20Systems#catalogue',
        'Explore aerospace & defence',
        'mechanical',
    ),
    (
        'hardware',
        'Hardware Systems',
        'Built around<br>the challenge.',
        'RF, high-speed digital hardware and modular processing platforms, designed for system integration.',
        'We develop high-density mixed-signal boards, VPX carrier modules, power/clock distribution units and precision phased-array structural assemblies from schematic to validation.',
        [
            'High-speed mixed-signal schematic & PCB layout',
            '3U / 6U OpenVPX & antenna-backplane hardware',
            'Power conditioning, thermal & structural engineering',
            'Bring-up, characterization & compliance testing',
        ],
        '/capabilities/#hardware',
        '/products/#catalogue',
        'Explore hardware systems',
        'rf',
    ),
    (
        'software',
        'Interactive Application Software',
        'Complex systems.<br>Clear interaction.',
        'Application interfaces, visualization and control software that connect people with engineering systems.',
        'Operator consoles, real-time radar display pipelines and AI inference runtimes bridge raw sensor telemetry with actionable situational awareness and diagnostics.',
        [
            'Real-time radar PPI / A-scope & telemetry displays',
            'Jetson, AMD & Intel AI inference integration',
            'System configuration, calibration & BIT tools',
            'High-throughput network data ingest & recording',
        ],
        '/capabilities/#software',
        '/products/?category=Radar%20%26%20AI%20Processing#catalogue',
        'Explore application software',
        'radar',
    ),
]

supporting = [
    ('integration', 'System Design & Integration', 'Architecture, interfaces and multidisciplinary integration from subsystem to system.'),
    ('collaboration', 'Industrial & Academic Collaboration', 'Working with industry and academia to connect research, development and engineering needs.'),
    ('manufacturing', 'Manufacturing & Testing Network', 'Coordinating fabrication, assembly and testing through a manufacturing and test network.'),
    ('prototyping', 'Concept & Prototype Development', 'Turning early requirements into concepts, prototypes and practical evaluation platforms.'),
]

domains = [
    (
        'defence',
        'Defence & Radar',
        'Connected platforms for radar and signal processing.',
        'Multichannel RF acquisition, phased-array antenna backplanes and modular VPX line replaceable units support the development of ground, naval and airborne sensing electronics.',
        '/assets/original/radar.webp',
        ['RF & Transceivers', 'Radar & AI Processing', 'Integrated Systems'],
    ),
    (
        'aerospace',
        'Aerospace',
        'Electronics for complex integration challenges.',
        'Compact 3U and 6U OpenVPX processing, programmable signal pipelines and high-speed optical backplanes address tight SWaP envelopes in aerospace avionics and flight-test instrumentation.',
        '/assets/original/mechanical.webp',
        ['RF & Transceivers', 'Radar & AI Processing', 'Integrated Systems'],
    ),
    (
        'space',
        'Space',
        'From RF signals to embedded intelligence.',
        'FPGA and embedded-system expertise supports high-reliability communication payloads, ground-segment baseband processing and mission-specific qualification workflows.',
        '/assets/original/rf.webp',
        ['RF & Transceivers', 'Radar & AI Processing'],
    ),
    (
        'industrial',
        'Industrial & Research',
        'A flexible foundation for experimentation and development.',
        'Configurable RFSoC, Versal, Agilex and Jetson hardware accelerates laboratory instrumentation, rapid waveform prototyping and advanced academic or industrial research.',
        '/assets/original/electronics.webp',
        ['RF & Transceivers', 'Radar & AI Processing', 'Radar Infrastructure'],
    ),
]

lifecycle = [
    ('Define', 'System requirements, link budgets, SWaP targets and interface architecture.'),
    ('Develop', 'Schematic/PCB design, VHDL/Verilog RTL, firmware and application software.'),
    ('Validate', 'Simulation, board bring-up, environmental stress and functional verification.'),
    ('Integrate', 'Chassis assembly, thermal qualification and full subsystem commissioning.'),
]


def supporting_html():
    return (
        '<section class="section supporting-section"><div class="wrap">'
        '<p class="eyebrow">SUPPORTING CAPABILITIES</p>'
        '<h2>From concept to integration.</h2>'
        '<div class="supporting-grid">'
        + ''.join(f'<article id="{key}"><h3>{title}</h3><p>{desc}</p></article>' for key, title, desc in supporting)
        + '</div></div></section>'
    )


def capabilities_page(cta: str) -> str:
    alias_map = {'embedded': 'fpga', 'hardware': 'systems'}
    lead = (
        '<section class="section expertise-intro"><div class="wrap">'
        '<p class="breadcrumb"><a href="/">Home</a> / Expertise</p>'
        '<p class="eyebrow">OUR EXPERTISE</p>'
        '<h1>Expertise across<br>the engineering lifecycle.</h1>'
        '<p class="expertise-lead">Advanced radars and RF solutions, embedded engineering, aerospace and defence, hardware systems and interactive application software.</p>'
        '</div></section>'
    )
    topics = []
    for i, (key, name, sub, _, detailed, points, _, cat_url, _, _) in enumerate(areas):
        alias = f'<span class="anchor-alias" id="{alias_map[key]}" aria-hidden="true"></span>' if key in alias_map else ''
        checks = ''.join(f'<li>{CHECK}<span>{pt}</span></li>' for pt in points)
        topics.append(
            f'<article class="expertise-topic" id="{key}">{alias}'
            f'<p class="eyebrow">{i + 1:02d} / OUR EXPERTISE</p>'
            f'<h2>{name}</h2>'
            f'<h3 class="expertise-sub">{sub.replace("<br>", " ")}</h3>'
            f'<p>{detailed}</p>'
            f'<ul class="check-list">{checks}</ul>'
            f'<div class="expertise-actions">'
            f'<a class="text-link" href="{cat_url}">Explore platforms ↗</a>'
            f'</div></article>'
        )
    details = f'<section class="section light"><div class="wrap expertise-sections">{"".join(topics)}</div></section>'
    process = (
        '<section class="section engineering-process-band"><div class="wrap">'
        '<div class="engineering-process">'
        '<p class="eyebrow">FROM CONCEPT TO INTEGRATION</p>'
        '<h2>One engineering conversation.<br>Every stage of development.</h2>'
        '<ol>'
        + ''.join(f'<li><span>0{i + 1}</span><h3>{title}</h3><p>{desc}</p></li>' for i, (title, desc) in enumerate(lifecycle))
        + '</ol></div></div></section>'
    )
    return lead + details + process + supporting_html() + cta


def applications_page(cta: str) -> str:
    lead = (
        '<section class="section expertise-intro"><div class="wrap">'
        '<p class="breadcrumb"><a href="/">Home</a> / What we do</p>'
        '<p class="eyebrow">WHAT WE DO</p>'
        '<h1>Engineering solutions across<br>defence and aerospace.</h1>'
        '<p class="expertise-lead">Configurable RF hardware, radar processors and integrated VPX systems tailored for demanding operational domains.</p>'
        '</div></section>'
    )
    domain_cards = []
    for i, (slug, name, heading, desc, img, cats) in enumerate(domains):
        tags = ''.join(
            f'<a href="/products/?category={quote(cat, safe="")}#catalogue">{cat} ↗</a>'
            for cat in cats
        )
        domain_cards.append(
            f'<article class="application-detail" id="{slug}">'
            f'<img src="{img}" alt="{name} application photograph" loading="lazy">'
            f'<div><p class="eyebrow">0{i + 1} / {name.upper()}</p>'
            f'<h2>{heading}</h2><p>{desc}</p>'
            f'<div class="application-tags">{tags}</div>'
            f'<a class="text-link" href="/contact/?application={slug}">Discuss your application ↗</a>'
            f'</div></article>'
        )
    domains_sec = f'<section class="section light"><div class="wrap">{"".join(domain_cards)}</div></section>'
    return lead + domains_sec + supporting_html() + cta


def apply():
    for f in D.rglob('*.html'):
        if f.name.startswith('__'):
            continue
        s = f.read_text(encoding='utf-8')
        s = s.replace('<link rel="stylesheet" href="/assets/refined.css">', '<link rel="stylesheet" href="/assets/refined.css"><link rel="stylesheet" href="/assets/home-update.css">')
        s = s.replace('<header class="site-header">', '<aside class="quick-update" aria-label="Latest information"><div><span class="update-dot"></span><strong>AVARTHANA UPDATE</strong><span>Explore our OpenVPX platforms and product documentation.</span><a href="/resources/">View downloads ↗</a></div></aside><header class="site-header">')

        if f == D / 'index.html':
            slides = ''
            for i, (_, title, h, desc, _, _, url, _, cta_label, img) in enumerate(areas):
                slides += (
                    f'<section class="banner-slide {"is-active" if i == 0 else ""}" data-slide="{i}" aria-hidden="{str(i != 0).lower()}" {"hidden" if i else ""}>'
                    f'<img class="banner-background hero-{img}" src="/assets/original/{img}.webp" alt="" {"loading=lazy" if i else "fetchpriority=high"}>'
                    f'<div class="wrap banner-content"><div class="banner-copy">'
                    f'<p class="eyebrow">AVARTHANA / {title.upper()}</p>'
                    f'<{"h2" if i else "h1"}>{h}</{"h2" if i else "h1"}>'
                    f'<p>{desc}</p><a class="hero-link" href="{url}">{cta_label} {AR}</a>'
                    f'</div></div></section>'
                )
            hero = (
                '<section class="epiq-banner expertise-banner" aria-roledescription="carousel" aria-label="Avarthana engineering expertise">'
                + slides
                + '<button class="banner-prev" aria-label="Previous area of expertise">‹</button>'
                + '<button class="banner-next" aria-label="Next area of expertise">›</button>'
                + '<div class="banner-controls"><div class="banner-dots">'
                + ''.join(f'<button aria-label="Show expertise {i + 1}" aria-pressed="{str(i == 0).lower()}" data-slide-to="{i}"></button>' for i in range(5))
                + '</div><button class="banner-pause" aria-label="Pause slideshow">II</button></div></section>'
            )
            intro = (
                '<section class="expertise-intro section"><div class="wrap"><p class="eyebrow">WHAT WE DO</p>'
                '<div class="portfolio-introduction"><h2>Engineering solutions.<br>Across defence<br>and aerospace.</h2>'
                '<div><p>Avarthana brings together advanced radars and RF solutions, embedded engineering, hardware systems and interactive application software for defence and aerospace applications.</p>'
                '<a class="text-link" href="/capabilities/">Discover our expertise ↗</a></div></div></div></section>'
            )
            data = [
                ('RF & acquisition', 'Multichannel transmit, receive and programmable signal processing.', '/products/?category=RF%20%26%20Transceivers', 'rf'),
                ('Radar & compute', 'FPGA and embedded processing platforms for demanding workloads.', '/products/?category=Radar%20%26%20AI%20Processing', 'electronics'),
                ('Integrated systems', 'Modular VPX systems, cooling and radar support infrastructure.', '/products/?category=Integrated%20Systems', 'mechanical'),
            ]
            cards = (
                '<section class="image-platforms section"><div class="wrap"><div class="section-heading">'
                '<div><p class="eyebrow">PRODUCTS & PLATFORMS</p><h2>Explore the engineering.</h2></div>'
                '<a href="/products/">All products ↗</a></div><div class="image-platform-grid">'
                + ''.join(f'<a class="image-platform" href="{url}"><img src="/assets/original/{img}.webp" alt="{title} photograph" loading="lazy"><div><h3>{title}</h3><p>{desc}</p></div><span class="card-arrow" aria-hidden="true">→</span></a>' for title, desc, url, img in data)
                + '</div></div></section>'
            )
            cta = re.search(r'<section class="contact-band".*?</section>', s, re.S).group()
            s = re.sub(r'<main id="main">.*?</main>', '<main id="main">' + hero + intro + cards + supporting_html() + cta + '</main>', s, flags=re.S)

        if f in (D / 'capabilities/index.html', D / 'applications/index.html'):
            cta_match = re.search(r'<section class="contact-band".*?</section>', s, re.S)
            cta = cta_match.group() if cta_match else ''
            is_what = f == D / 'applications/index.html'
            body = applications_page(cta) if is_what else capabilities_page(cta)
            s = re.sub(r'<main id="main">.*?</main>', '<main id="main">' + body + '</main>', s, flags=re.S)
            page_title = 'What We Do | Avarthana Technologies' if is_what else 'Engineering Expertise | Avarthana Technologies'
            s = re.sub(r'<title>.*?</title>', f'<title>{page_title}</title>', s)

        s = s.replace('↗', '<svg class="icon inline-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M6 18 18 6M6 6h12v12"/></svg>')
        f.write_text(s, encoding='utf-8')
    print('Updated header, expertise-led homepage and product pathways')
