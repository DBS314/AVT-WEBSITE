from pathlib import Path
from html import escape as e
from urllib.parse import quote
import json,re
D=Path(__file__).parent/'dist';P=json.loads((D.parent/'products.json').read_text())
C=[('RF & Transceivers','Multichannel RF acquisition and transmit / receive platforms.'),('Radar & AI Processing','FPGA and embedded computing for radar and signal processing.'),('Integrated Systems','Modular, air-cooled and liquid-cooled VPX systems.'),('Radar Infrastructure','Structures and mechanical support for phased-array installations.')]
A='<svg class="icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>'
def url(cat):return '/products/?category='+quote(cat,safe='')+'#catalogue'
def apply():
 for f in D.rglob('*.html'):
  if f.name.startswith('__'):continue
  s=f.read_text().replace('<link rel="stylesheet" href="/assets/home-update.css">','<link rel="stylesheet" href="/assets/home-update.css"><link rel="stylesheet" href="/assets/cohesion.css">')
  mobile='<nav id="mobile-nav" class="mobile-nav" aria-label="Mobile navigation" hidden><a href="/applications/">What we do</a><details><summary>Products</summary><a href="/products/">All products</a>'+''.join(f'<a href="{url(name)}">{e(name)}</a>' for name,_ in C)+'</details><a href="/company/">Company</a><a href="/resources/">Resources</a><a href="/capabilities/">Expertise</a><a class="mobile-contact-btn" href="/contact/">Contact us</a></nav>'
  s=re.sub(r'<nav id="mobile-nav".*?</nav>',mobile,s,flags=re.S)
  if f==D/'products/index.html':
   intro='<section class="portfolio-hero"><div class="wrap"><p class="breadcrumb"><a href="/">Home</a> / Products</p><div class="portfolio-hero-grid"><div><p class="eyebrow">PRODUCTS & PLATFORMS</p><h1>From signal.<br>To system.</h1><p class="portfolio-lead">RF acquisition, programmable processing and integrated hardware. Find a platform for your defence and aerospace application.</p><a class="text-link" href="/downloads/avarthana-product-catalogue.pdf" download>Download product catalogue '+A+'</a></div><nav class="category-directory" aria-label="Product categories"><p class="eyebrow">EXPLORE BY CATEGORY</p>'+''.join(f'<a href="{url(name)}"><div><h2>{e(name)}</h2><p>{desc}</p></div><span>{sum(p["category"]==name for p in P):02d}</span>{A}</a>' for name,desc in C)+'</nav></div></div></section>'
   s=re.sub(r'<section class="page-intro dark">.*?</section>',intro,s,count=1,flags=re.S)
   s=s.replace('<section class="section catalogue-section light">','<section class="section catalogue-section light" id="catalogue"><div class="wrap catalogue-section-heading"><p class="eyebrow">THE PRODUCT PORTFOLIO</p><h2>Find your platform.</h2><p>Search and filter products by category, form factor, or processing platform. Each platform includes specifications and downloadable documentation.</p></div>')
   s=s.replace('Product family</legend>','Product category</legend>')
  # Shared naming keeps every route consistent with the navigation.
  s=s.replace('>Engineering capabilities</a>','>Engineering expertise</a>').replace('>Applications</a>','>What we do</a>').replace('>Applications & engineering</a>','>What we do</a>')
  s=s.replace('>Datasheets & downloads</a>','>Documentation & downloads</a>')
  if f==D/'company/index.html':
   s=s.replace('Electronics engineering from Bengaluru, India.','Engineering solutions across defence and aerospace, from Bengaluru, India.')
  if f==D/'applications/index.html':
   s=s.replace('<a class="nav-trigger" href="/applications/"','<a class="nav-trigger active" aria-current="page" href="/applications/"',1)
   s=s.replace('<a href="/applications/">What we do</a>','<a class="active" aria-current="page" href="/applications/">What we do</a>',1)
  elif f==D/'products/index.html':
   s=s.replace('<a class="nav-trigger" href="/products/"','<a class="nav-trigger active" aria-current="page" href="/products/"',1)
   s=s.replace('<a href="/products/">All products</a>','<a class="active" aria-current="page" href="/products/">All products</a>',1)
  elif f.parent.parent==D/'products' and f.name=='index.html':
   s=s.replace('<a class="nav-trigger" href="/products/"','<a class="nav-trigger active" href="/products/"',1)
  elif f==D/'company/index.html':
   s=s.replace('<a class="nav-trigger" href="/company/"','<a class="nav-trigger active" aria-current="page" href="/company/"',1)
   s=s.replace('<a href="/company/">Company</a>','<a class="active" aria-current="page" href="/company/">Company</a>',1)
  elif f==D/'resources/index.html':
   s=s.replace('<a class="nav-trigger" href="/resources/"','<a class="nav-trigger active" aria-current="page" href="/resources/"',1)
   s=s.replace('<a href="/resources/">Resources</a>','<a class="active" aria-current="page" href="/resources/">Resources</a>',1)
  elif f==D/'capabilities/index.html':
   s=s.replace('<a href="/capabilities/">Expertise</a>','<a class="active" aria-current="page" href="/capabilities/">Expertise</a>')
  if f.parent.parent==D/'products' and f.name=='index.html':
   # Useful documentation links remain on the product page; diagrams stay download-only.
   s=s.replace('PLATFORM OVERVIEW','PRODUCT OVERVIEW').replace('The details.<br>Ready to download.','Product documentation.')
  f.write_text(s)
 print('Unified catalogue, category navigation and shared content hierarchy')
