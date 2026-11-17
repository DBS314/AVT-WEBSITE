"""Extract Rev 03 hardware renders and full specifications into products.json."""
from io import BytesIO
from pathlib import Path
import json
import re
import fitz
from PIL import Image, ImageChops, ImageFilter

ROOT = Path(__file__).parent
DIST = ROOT / 'dist'
DL = DIST / 'downloads'
PRODUCTS_IMG_DIR = DIST / 'assets' / 'products'

GROUP_TITLES = {
    'PROCESSING AND MEMORY': 'Processing & memory',
    'OPTICAL, ETHERNET AND DIGITAL I/O': 'Optical, Ethernet & digital I/O',
    'CLOCK AND SYNCHRONIZATION': 'Clock & synchronization',
    'POWER AND OPENVPX INTEGRATION': 'Power & OpenVPX integration',
    'MONITORING, THERMAL AND DIAGNOSTICS': 'Monitoring, thermal & diagnostics',
    'RELIABILITY AND QUALIFICATION TARGETS': 'Reliability & qualification targets',
    'ANTENNA AND MATERIALS': 'Antenna & materials',
    'RF FRONT-END TARGETS': 'RF front-end targets',
    'RF ACQUISITION AND PACKAGING': 'RF acquisition & packaging',
    'ANTENNA-BACKPLANE INTEGRATION': 'Antenna-backplane integration',
    'COMPUTE, MEMORY AND STORAGE': 'Compute, memory & storage',
    'NETWORKING AND EXPANSION': 'Networking & expansion',
    'CONTROL AND DISPLAY': 'Control & display',
    'SYSTEM INTEGRATION': 'System integration',
}


def crop_white_margins(img: Image.Image, pad: int = 32, threshold: int = 24) -> Image.Image:
    """Trim uniform near-white borders around a hardware render."""
    bg = Image.new('RGB', img.size, 'white')
    diff = ImageChops.difference(img, bg).convert('L').point(lambda v: 255 if v > threshold else 0)
    if img.width > 1000:
        diff = diff.filter(ImageFilter.MinFilter(3))
    bbox = diff.getbbox()
    if not bbox:
        return img
    return img.crop((
        max(0, bbox[0] - pad),
        max(0, bbox[1] - pad),
        min(img.width, bbox[2] + pad),
        min(img.height, bbox[3] + pad),
    ))


def extract_webp_render(code: str, slug: str) -> str:
    """Extract hardware render from Page 1 of a Rev 03 datasheet as a .webp file."""
    pdf_path = DL / f'{code}.pdf'
    out_path = PRODUCTS_IMG_DIR / f'{slug}.webp'
    with fitz.open(pdf_path) as doc:
        page = doc[0]
        if code in ('T5_P12', 'T5_P13'):
            # Antenna-array + RFSiP + exploded stackup illustration on Page 1.
            clip = fitz.Rect(42, 180, 555, 355)
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=clip, alpha=False)
            img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        else:
            candidates = [
                im for im in page.get_images(full=True)
                if im[2] >= 1200 and im[3] >= 800
            ]
            if not candidates:
                raise RuntimeError(f'No large hardware render found in {pdf_path}')
            best = max(candidates, key=lambda im: im[2] * im[3])
            imdata = doc.extract_image(best[0])
            img = Image.open(BytesIO(imdata['image'])).convert('RGB')
        img = crop_white_margins(img)
        img.save(out_path, quality=94)
    return f'/assets/products/{slug}.webp'


def clean_line_join(lines: list[str]) -> str:
    """Join wrapped PDF lines cleanly."""
    return re.sub(r'\s+', ' ', ' '.join(lines)).strip()


def extract_highlights(page: fitz.Page) -> list[str]:
    """Extract the six Page 1 PRODUCT HIGHLIGHTS pairs in top-to-bottom, left-to-right order."""
    blocks = [
        b for b in page.get_text('blocks')
        if b[6] == 0 and b[1] >= 605 and b[1] < 760 and 45 < b[0] < 520
    ]
    # Group by (row_bucket, column_bucket): left col ~53, right col ~320.
    # Titles are around y=615, 670, 725; bodies around y=634, 689, 744.
    rows = [615, 670, 725]
    cols = [53, 320]
    highlights = []
    for r_y in rows:
        for c_x in cols:
            pair = [
                b for b in blocks
                if abs(b[0] - c_x) < 40 and (r_y - 10) <= b[1] <= (r_y + 35)
            ]
            pair.sort(key=lambda b: b[1])
            if len(pair) >= 2:
                title = clean_line_join(pair[0][4].splitlines())
                body = clean_line_join(pair[1][4].splitlines())
                highlights.append(f'{title}: {body}')
    return highlights


def extract_specs(doc: fitz.Document) -> dict[str, list[list[str]]]:
    """Extract grouped specification tables from Pages 3 and 4 of a Rev 03 PDF."""
    specs: dict[str, list[list[str]]] = {}
    for pno in (2, 3):
        if pno >= len(doc):
            continue
        page = doc[pno]
        blocks = [
            b for b in page.get_text('blocks')
            if b[6] == 0 and 112 < b[1] < 690
        ]
        blocks.sort(key=lambda b: (round(b[1], 1), b[0]))
        current_group = None
        i = 0
        while i < len(blocks):
            b = blocks[i]
            x0, y0 = b[0], b[1]
            lines = [ln.strip() for ln in b[4].strip().splitlines() if ln.strip()]
            joined = clean_line_join(lines)

            # Skip footers, disclaimers, and URL lines.
            if (
                joined.startswith('Device resources')
                or joined.startswith('Preliminary configuration')
                or 'REV 03' in joined
                or 'web: avarthana.com' in joined
                or x0 > 250
            ):
                i += 1
                continue

            # Section header blocks sit at x0 ~ 41 and are uppercase.
            if x0 < 45 and joined == 'CONFIGURATION':
                current_group = None
                i += 1
                continue
            if x0 < 45 and joined in GROUP_TITLES:
                current_group = GROUP_TITLES[joined]
                specs.setdefault(current_group, [])
                i += 1
                continue

            # Specification row blocks sit around x0 ~ 49.
            if current_group and 45 <= x0 <= 60:
                # Check if value is in an adjacent right-hand block at the same y (~204).
                if i + 1 < len(blocks) and abs(blocks[i + 1][1] - y0) < 6 and blocks[i + 1][0] > 180:
                    key = clean_line_join(lines)
                    val_lines = [ln.strip() for ln in blocks[i + 1][4].strip().splitlines() if ln.strip()]
                    val = clean_line_join(val_lines)
                    specs[current_group].append([key, val])
                    i += 2
                    continue
                if len(lines) >= 2:
                    key = lines[0]
                    val = clean_line_join(lines[1:])
                    specs[current_group].append([key, val])
                    i += 1
                    continue

            i += 1
    return {k: v for k, v in specs.items() if v}


def clean_string(text: str) -> str:
    """Fix OCR spacing/hyphenation glitches in legacy brochure text."""
    replacements = [
        ('real- time', 'real-time'),
        ('phased- array', 'phased-array'),
        ('element- control', 'element-control'),
        ('RS- 232/485', 'RS-232/485'),
        ('2 × 1 Gigabit Ethernet 10 Gigabit Ethernet', '2 × 1 Gigabit Ethernet, 1 × 10 Gigabit Ethernet'),
        (
            'FireFly optical interface 8 × GTY lanes, up to 25 Gbps per lane',
            'FireFly optical interface (8 × GTY lanes, up to 25 Gbps per lane)',
        ),
        (
            '8 × GTY lanes connected to optical data interface Up to 25 Gbps per lane',
            '8 × GTY lanes connected to optical data interface (up to 25 Gbps per lane)',
        ),
        (
            'Onboard clock generator Dedicated PS and PL domain clocks',
            'Onboard clock generator; dedicated PS and PL domain clocks',
        ),
        (
            'Onboard clock generator Dedicated processing and logic domain clocks',
            'Onboard clock generator; dedicated processing and logic domain clocks',
        ),
        (
            'Onboard clock generator External clock connections',
            'Onboard clock generator; external clock connections',
        ),
        (
            'Synchronization bus VPX reference clock and auxiliary clock connections',
            'Synchronization bus, VPX reference clock and auxiliary clock connections',
        ),
        (
            'VPX reference clock and auxiliary clock connections P2 reference clock connection',
            'VPX reference clock, auxiliary clock and P2 reference clock connections',
        ),
        (
            '4 × RF inputs and 4 × RF outputs at P2 Reference clock connection',
            '4 × RF inputs, 4 × RF outputs and reference clock connection at P2',
        ),
        (
            'Synchronization bus, VPX reference and auxiliary clocksAntenna trigger and reference-clock connections',
            'Synchronization bus, VPX reference and auxiliary clocks; antenna trigger and reference-clock connections',
        ),
    ]
    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    if out == 'processing system (PS) and programmable logic (PL)':
        out = 'Integrated processing system (PS) and programmable logic (PL)'
    return out


def main() -> None:
    products = json.loads((ROOT / 'products.json').read_text(encoding='utf-8'))

    # Clean legacy spec strings and highlights in products 1..15.
    for p in products:
        if p['id'] <= 15:
            p['description'] = [clean_string(d) for d in p['description']]
            p['highlights'] = [clean_string(h) for h in p['highlights']]
            for group, rows in p['specs'].items():
                for row in rows:
                    row[1] = clean_string(row[1])

    # Specific fixes for Product 11 (6u-phased-array-rfsoc).
    p11 = next(p for p in products if p['id'] == 11)
    for row in p11['specs'].get('Digital interfaces & memory', []):
        if row[0] == 'Storage Interfaces' and row[1] == '&':
            row[1] = 'microSD card slot and M.2 SSD interface'
    backplane_rows = p11['specs'].get('Backplane & service', [])
    new_backplane = []
    for k, v in backplane_rows:
        if k == 'VPX Connections' and 'Antenna Backplane Interfaces' in v:
            new_backplane.append(['VPX Connections', 'P0, P1 and P2'])
            new_backplane.append([
                'Antenna Backplane Interfaces',
                'Optical data, element control, trigger, reference clock and 16-channel Tx/Rx RF connections',
            ])
        else:
            new_backplane.append([k, v])
    p11['specs']['Backplane & service'] = new_backplane

    # Specific cleanup and metadata for Products 13, 14, 15.
    p13 = next(p for p in products if p['id'] == 13)
    p13['document_code'] = 'LRU-LC'
    p13['document_revision'] = 'System datasheet · 2 pages'
    p13['document_pages'] = {'datasheet': 2, 'diagram_pdf': 1}
    p13['highlights'] = [
        'Modular 13-card VPX configuration: Combines 8 × 6U RFSoC cards, 2 × 6U Versal cards, 1 × Clock Distribution & I/O card and 2 × Power cards.',
        'Monitored liquid cooling: Conduction-cooled cards mated to a chassis cold-wall with liquid coolant inlet, outlet and flow monitoring.',
        'Quick-disconnect thermal interface: Cold-wall couplings and sensor provisions (level, pressure, temperature and flow) for reliable heat rejection.',
        'Rugged CNC-machined enclosure: Slot-mounted Aluminum 6061-T6 chassis (830 × 340 × 240 mm, 35 kg empty).',
        'System-level synchronization: Shared backplane timing, trigger distribution, control bus and high-speed inter-card links.',
        'Environmental readiness: Designed for −10°C to +60°C operating temperature and −51°C to +85°C storage temperature.',
    ]

    p14 = next(p for p in products if p['id'] == 14)
    p14['document_code'] = 'LRU-AC'
    p14['document_revision'] = 'System datasheet · 2 pages'
    p14['document_pages'] = {'datasheet': 2, 'diagram_pdf': 1}
    p14['highlights'] = [
        'Modular 13-card VPX configuration: Combines 8 × 6U RFSoC cards, 2 × 6U Versal cards, 1 × Clock Distribution & I/O card and 2 × Power cards.',
        'VITA 48.1 forced-air cooling: Integrated high-performance fans, heat sinks and filtered inlet-to-exhaust airflow channels.',
        'Continuous thermal monitoring: Built-in temperature sensing and airflow management across all populated VPX slots.',
        'Rugged CNC-machined enclosure: Slot-mounted Aluminum 6061-T6 chassis (830 × 340 × 240 mm, 35 kg empty).',
        'System-level synchronization: Shared backplane timing, trigger distribution, control bus and high-speed inter-card links.',
        'Environmental readiness: Designed for −10°C to +60°C operating temperature and −51°C to +85°C storage temperature.',
    ]

    p15 = next(p for p in products if p['id'] == 15)
    p15['document_code'] = 'RSS-3X3'
    p15['document_revision'] = 'Structural datasheet · 2 pages'
    p15['document_pages'] = {'datasheet': 2}
    p15['highlights'] = [
        '3 × 3 phased-array framework: Supports up to nine antenna modules (up to 1 m × 1 m per module) and protective radome.',
        '3,000 × 3,000 × 3,000 mm steel structure: Primary 80 × 80 × 5 SHS alloy steel columns and 40 × 40 × 4 SHS top cage members with X-bracing on all four faces.',
        'Foundation & alignment stability: Grouted pocket base conditions and precision mounting interfaces for radar alignment and servicing.',
        'Cooling & thermal provisions: Integrated routing provisions for liquid-cooling CDU lines and thermal bridging for structural beams.',
    ]

    # Product 10 (T4_P10) and Products 16..21 (T5_P12..T7_P18): extract Rev 03 specs & highlights.
    rev03_overrides = {
        16: {
            'processor': 'AMD Versal RFSoC',
            'channels': 16,
            'metrics': [
                ['Sub-array', '4 × 4 (16 ch)'],
                ['Receive gain', '65 ±15 dB'],
                ['Noise figure', '~1 dB'],
                ['Architecture', 'Versal RFSoC'],
            ],
        },
        17: {
            'processor': 'Agilex FPGA',
            'channels': 16,
            'metrics': [
                ['Sub-array', '4 × 4 (16 ch)'],
                ['Receive gain', '65 ±15 dB'],
                ['Noise figure', '~1 dB'],
                ['Architecture', 'Agilex FPGA'],
            ],
        },
        18: {
            'processor': 'AMD Versal FPGA',
            'metrics': [
                ['PL + PS memory', '32 + 16 GB'],
                ['Optical I/O', '64 lanes'],
                ['Ethernet', '3 × 25G + 10GbE'],
                ['Architecture', 'AMD Versal'],
            ],
        },
        19: {
            'processor': 'Agilex FPGA',
            'metrics': [
                ['PL + PS memory', '32 + 16 GB'],
                ['Optical I/O', '64 lanes'],
                ['Ethernet', '3 × 25G + 10GbE'],
                ['Architecture', 'Agilex FPGA'],
            ],
        },
        20: {
            'processor': 'AMD Processor',
            'metrics': [
                ['System memory', '64 GB LPDDR5'],
                ['Networking', '1/10/40/100GbE'],
                ['PCIe expansion', '22 lanes'],
                ['Display', '8K60 multi-mode'],
            ],
        },
        21: {
            'processor': 'Intel Processor',
            'metrics': [
                ['System memory', '64 GB LPDDR5'],
                ['Networking', '1/10/40/100GbE'],
                ['PCIe expansion', '22 lanes'],
                ['Display', '8K60 multi-mode'],
            ],
        },
    }

    for p in products:
        pid = p['id']
        if pid == 10 or pid >= 16:
            code = p['document_code']
            pdf_path = DL / f'{code}.pdf'
            with fitz.open(pdf_path) as doc:
                extracted_highlights = extract_highlights(doc[0])
                extracted_specs = extract_specs(doc)
            if extracted_highlights:
                p['highlights'] = extracted_highlights
            if extracted_specs:
                p['specs'] = extracted_specs
            if pid >= 16:
                p['image'] = extract_webp_render(code, p['slug'])
                for field, value in rev03_overrides[pid].items():
                    p[field] = value

    (ROOT / 'products.json').write_text(json.dumps(products, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (DIST / 'assets' / 'products.json').write_text(json.dumps(products, ensure_ascii=False), encoding='utf-8')
    print(f'Updated {len(products)} products and extracted renders for IDs 16-21.')


if __name__ == '__main__':
    main()
