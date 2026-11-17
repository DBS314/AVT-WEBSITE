"""Extract Avarthana-owned catalogue content and assets from the supplied brochure."""
from pathlib import Path
from io import BytesIO
import fitz, json, re, shutil
from PIL import Image

ROOT = Path(__file__).parent
DIST = ROOT / 'dist'
SOURCE = ROOT / 'AVARTHANA BROUCHERS.pdf'
pdf = fitz.open(SOURCE)

# Titles distinguish each product without introducing unverified model numbers.
definitions = [
 ('6u-openvpx-rfsoc','6U OpenVPX RFSoC','Multi-channel transmit & receive','RF & Transceivers','6U','RFSoC','XCZU49DR',16,'Integrated RF acquisition, waveform generation and real-time signal processing.'),
 ('6u-openvpx-versal-rfsoc','6U OpenVPX Versal RFSoC','Multi-channel transmit & receive','RF & Transceivers','6U','Versal','AMD Versal',16,'Versal-based RF conversion and programmable processing for multichannel systems.'),
 ('6u-openvpx-agilex','6U OpenVPX Agilex FPGA','Multi-channel transmit & receive','RF & Transceivers','6U','Agilex','Agilex 9 AGRW039',16,'Parallel FPGA processing with sixteen RF inputs and sixteen RF outputs.'),
 ('6u-openvpx-versal-radar','6U OpenVPX Versal','Radar signal & data processing','Radar & AI Processing','6U','Versal','AMD Versal',None,'Configurable parallel radar processing, data handling and system control.'),
 ('6u-openvpx-agilex-radar','6U OpenVPX Agilex FPGA','Radar signal & data processing','Radar & AI Processing','6U','Agilex','Agilex FPGA',16,'Integrated RF conversion and FPGA processing for radar signal chains.'),
 ('3u-openvpx-rfsoc','3U OpenVPX RFSoC','Multi-channel transmit & receive','RF & Transceivers','3U','RFSoC','XCZU49DR',8,'Eight-channel RF acquisition and waveform generation in a compact 3U platform.'),
 ('3u-openvpx-versal-rfsoc','3U OpenVPX Versal RFSoC','Multi-channel transmit & receive','RF & Transceivers','3U','Versal','AMD Versal',8,'Compact multichannel RF conversion with dedicated processing and logic resources.'),
 ('3u-openvpx-agilex','3U OpenVPX Agilex FPGA','Multi-channel transmit & receive','RF & Transceivers','3U','Agilex','Agilex 9 AGRW039',8,'Eight RF inputs and outputs with configurable processing on Agilex 9.'),
 ('3u-openvpx-versal-radar','3U OpenVPX Versal','Radar signal & data processing','Radar & AI Processing','3U','Versal','AMD Versal',None,'Radar data handling and parallel signal processing in a compact 3U footprint.'),
 ('3u-openvpx-agilex-radar','3U OpenVPX Agilex FPGA','Radar signal & data processing','Radar & AI Processing','3U','Agilex','Agilex 9 AGRW014',None,'Direct RF-series SoC FPGA processing with embedded Arm resources.'),
 ('6u-phased-array-rfsoc','6U Phased-array RFSoC','Antenna backplane processing','RF & Transceivers','6U','RFSoC','XCZU49DR',16,'RF conversion and digital radar processing with antenna backplane connectivity.'),
 ('nvidia-jetson-radar','NVIDIA Jetson Radar Processor','Tracking, perception & AI inference','Radar & AI Processing','VPX carrier','Jetson','NVIDIA Jetson',None,'Radar data processing, object tracking and trained-model inference on Jetson.'),
 ('6u-liquid-cooled-lru','6U Liquid-cooled LRU','Integrated line replaceable unit','Integrated Systems','6U','System','RFSoC + Versal',None,'A modular RFSoC and Versal system with a monitored liquid-cooling path.'),
 ('6u-air-cooled-lru','6U Air-cooled LRU','Integrated line replaceable unit','Integrated Systems','6U','System','RFSoC + Versal',None,'A modular VPX card configuration in a forced-air-cooled chassis.'),
 ('radar-support-structure','Radar Support Structure','Phased-array installation framework','Radar Infrastructure','3 × 3 array','Structure','Steel framework',None,'A braced steel mounting framework for a phased-array antenna and radome.')
]

labels = [
 'Number of Receive Channels','Number of Transmit Channels','Backplane RF Connections',
 'Optical Backplane Interface','RF Backplane Interface','Processing Architecture',
 'Signal Processing Architecture','External Timing Inputs','Processing Resources',
 'Processing Device','Processing Platform','Embedded Processor','Application Functions',
 'Application Workloads','Processing Function','Software Functions','Data Connectivity',
 'System Memory Capacity','Nonvolatile Memory','Removable Storage','Storage Interfaces',
 'Ethernet Interfaces','Peripheral Interfaces','Service Connections','Status Indication',
 'Input Interface','Output Interface','Data Conversion','Form Factor','Power Input',
 'PS Memory','PL Memory','Optical Interface','Digital I/O','Data Interfaces','System Functions',
 'Timing Input','Clock Generation','Backplane Timing','Backplane Synchronization','VPX Connections',
 'Debug Interfaces','SSD Interface','Digital Interface','USB Interface','Serial Interface',
 'Cooling Method','Chassis material','VPX slot count','Populated slots','Coolant type',
 'Coolant inlet temperature','Coolant outlet temperature','Maximum working temperature',
 'Cold-Wall interface','Operating temperature range','Storage temperature range','Airflow arrangement',
 'Length','Width','Height','Mass','Construction','Mounting','Cards',
 'FootPrint','Primary columns','Top cage members','Bracing','Base condition',
 'IS 800:2007','IS 875','IS 4923'
]
pattern = re.compile(r'(?<![\w-])('+'|'.join(re.escape(s) for s in sorted(labels,key=len,reverse=True))+r')(?=\s|$)')
def clean(s): return re.sub(r'\s+',' ',s).strip()

def table_groups(page, idx):
 groups = {}
 for b in page.get_text('blocks'):
  if not ((35 if idx==14 else 285) < b[1] < 690): continue
  s = clean(b[4])
  if idx<12:
   if b[1]<410:
    group='General' if b[0]<190 else ('RF receiver' if b[0]<385 else 'RF transmitter')
    if idx in (3,8):group='General' if b[0]<190 else ('Radar signal processing' if b[0]<385 else 'Radar data processing')
    if idx==11:group='AI processing' if 'Processing Function' in s else ('General' if b[0]<210 else 'Radar data processing')
   elif b[1]<532: group='Digital interfaces & memory'
   else: group='Clock & synchronization' if b[0]<300 else 'Backplane & service'
  elif idx<14:
   group='General' if b[0]<190 and b[1]<570 else ('Environmental' if b[1]>570 else ('Mechanical architecture' if b[0]<390 else 'Thermal & cooling'))
  else:
   group='General' if b[0]<190 else ('Structure' if b[0]<390 else 'Standards listed')
  matches=list(pattern.finditer(s))
  for j,m in enumerate(matches):
   value=s[m.end(): matches[j+1].start() if j+1<len(matches) else len(s)].replace('DIGITAL SPECIFICATIONS','').strip()
   if value: groups.setdefault(group,[]).append([m.group(),value])
 return groups

items=[]
for idx,definition in enumerate(definitions):
 slug,title,subtitle,category,form,family,processor,channels,summary=definition
 p1,p2=pdf[idx*2],pdf[idx*2+1]
 # Product renders are embedded at full resolution, independent of page typography.
 image_candidates=[]
 for im in p1.get_images(full=True):
  rects=p1.get_image_rects(im[0])
  if any(70<r.y0<210 and r.y1>300 for r in rects):image_candidates.append(im)
 imdata=pdf.extract_image(max(image_candidates,key=lambda x:x[2]*x[3])[0])
 img=Image.open(BytesIO(imdata['image'])).convert('RGB')
 # Trim blank margins for more legible product presentation; retain the exact hardware rendering.
 from PIL import ImageChops, ImageFilter
 bbox=ImageChops.difference(img,Image.new('RGB',img.size,'white')).convert('L').point(lambda v:255 if v>35 else 0).filter(ImageFilter.MinFilter(15 if img.width>1000 else 3)).getbbox()
 if bbox:img=img.crop((max(0,bbox[0]-35),max(0,bbox[1]-35),min(img.width,bbox[2]+35),min(img.height,bbox[3]+35)))
 img.save(DIST/'assets/products'/f'{slug}.webp',quality=94)
 # Extract the original engineering block diagram, avoiding upscaled screenshots.
 diagram=None
 for im in p2.get_images(full=True):
  if any(35<r.y0<100 and r.y1<300 and r.width>300 for r in p2.get_image_rects(im[0])):
   diagram=f'/assets/diagrams/{slug}.png'; d=pdf.extract_image(im[0]);(DIST/diagram.lstrip('/')).write_bytes(d['image']);break
 # Each downloadable PDF is an unmodified pair of pages from the supplied brochure.
 doc=fitz.open();doc.insert_pdf(pdf,from_page=idx*2,to_page=idx*2+1)
 doc.save(DIST/'downloads'/f'{slug}.pdf',garbage=4,deflate=True);doc.close()
 desc=[];high=[]
 for b in p1.get_text('blocks'):
  s=clean(b[4])
  if 440<b[1]<580: desc.append(s)
  elif b[1]>600 and b[0]>70:
   # The six board highlights use label-colon boundaries.
   high.extend([clean(t) for t in re.split(r'(?<=[.])\s+(?=[A-Z0-9])',s) if t])
 groups=table_groups(p2,idx)
 if idx==14:
  groups={
   'General':[['Module array','3 × 3, up to 1 m × 1 m per antenna'],['Cooling provision','CDU and routing']],
   'Structure':[['Mass','1,451.28 kg'],['Footprint','3,000 × 3,000 mm'],['Height','3,000 mm'],['Primary columns','80 × 80 × 5 SHS, Alloy Steel (IS 4923)'],['Top cage members','40 × 40 × 4 SHS + 33 mm diameter rod diagonals'],['Construction','Welding / fasteners'],['Bracing','X-bracing on all four faces'],['Base condition','Grouted pocket']],
   'Standards listed':[['IS 800:2007','Steel structure design checks'],['IS 875','Building and structure design loads, other than earthquake'],['IS 4923','Hollow steel section properties']]}
 notes=[]
 if idx==9:
  # Two brochure pages disagree on RF channels, rates and memory. Do not choose a value silently.
  desc=['A compact 3U OpenVPX radar signal and data processing platform based on the Agilex 9 Direct RF-Series SoC FPGA AGRW014. It combines programmable logic with embedded Arm processing for configurable RF and radar applications.']
  high=['Agilex 9 AGRW014 Direct RF-Series SoC FPGA','Quad-core Arm Cortex-A53 embedded processing','Configurable radar signal and data processing','OpenVPX integration in a 3U form factor']
  groups={
   'General':[['Form Factor','3U OpenVPX'],['Processing Device','Agilex 9 Direct RF-Series SoC FPGA AGRW014'],['Embedded Processor','Quad-core Arm Cortex-A53, up to 1.5 GHz']],
   'RF conversion & memory':[['RF channel configuration','Confirm with engineering'],['Converter sample rate','Confirm with engineering'],['PS / PL memory capacity','Confirm with engineering']],
   'Integration':[['VPX Connections','P0, P1 and P2'],['Storage Interfaces','microSD card slot and M.2 SSD interface'],['Debug Interfaces','JTAG and UART-to-USB']]}
  notes=['RF channel count, converter sample rate and memory capacity are under review. Contact engineering for confirmed specifications.']
 if idx in (12,13):
  desc=[('A 6U VPX line replaceable unit with '+('liquid cooling' if idx==12 else 'forced-air cooling')+'. The documented configuration combines eight RFSoC cards, two Versal cards, one clock distribution and I/O card, and two power cards. The chassis supports system integration through shared power, timing, control and inter-card connectivity.')]
  for rows in groups.values():
   for row in rows:
    if row[0]=='VPX slot count':row[1]='Confirm with engineering'
    if row[0]=='Populated slots':row[1]='13 cards: 8 RFSoC + 2 Versal + 1 Clock I/O + 2 Power'
  notes=['The populated configuration contains 13 cards. Total backplane slot capacity is under review.']
 metrics=([['RF inputs',str(channels)],['RF outputs',str(channels)],['PS + PL memory','16 + 16 GB'],['Form factor',form]] if channels else [['Architecture',family],['Form factor',form],['Platform',processor],['Integration','OpenVPX' if idx<12 else 'System-level']])
 if idx in (3,8):metrics=[['Processing','AMD Versal'],['PS + PL memory','16 + 16 GB'],['Optical lanes','8 × 25 Gbps'],['Form factor',form]]
 if idx==9:metrics=[['Device','AGRW014'],['Processing','Arm Cortex-A53'],['Form factor','3U OpenVPX'],['RF configuration','Under review']]
 if idx==11:metrics=[['Compute','NVIDIA Jetson'],['System memory','16 GB'],['Network','10 GbE'],['Application','Radar & AI']]
 if idx in (12,13):metrics=[['Card configuration','13 cards'],['RFSoC + Versal','8 + 2 cards'],['Cooling','Liquid' if idx==12 else 'Forced air'],['Form factor','6U VPX']]
 if idx==14:metrics=[['Module array','3 × 3'],['Footprint','3 × 3 m'],['Height','3 m'],['Structure','Braced steel']]
 items.append(dict(id=idx+1,slug=slug,title=title,subtitle=subtitle,category=category,form=form,family=family,processor=processor,channels=channels,summary=summary,description=desc,highlights=high,specs=groups,notes=notes,metrics=metrics,image=f'/assets/products/{slug}.webp',diagram=diagram,datasheet=f'/downloads/{slug}.pdf'))

(ROOT/'products.json').write_text(json.dumps(items,indent=2,ensure_ascii=False))
(DIST/'assets/products.json').write_text(json.dumps(items,ensure_ascii=False))
shutil.copyfile(SOURCE,DIST/'downloads/avarthana-product-catalogue.pdf')
print(json.dumps({'products':len(items),'images':len(list((DIST/'assets/products').glob('*.webp'))),'diagrams':len(list((DIST/'assets/diagrams').glob('*.png'))),'pdfs':len(list((DIST/'downloads').glob('*.pdf')))}))
