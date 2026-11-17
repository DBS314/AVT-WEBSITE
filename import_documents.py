from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from html import escape
import json,csv,io,re,fitz,sys
ROOT=Path(__file__).parent;D=ROOT/'dist';out=D/'downloads';P=json.loads((ROOT/'products.json').read_text())
source=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'Avarthana_All_Products_Updated_Letterhead.zip'
new={12:('phased-array-versal-rfsoc','Phased-Array Versal RFSoC Tx/Rx','RF & Transceivers','Versal'),13:('phased-array-agilex-transceiver','Phased-Array Agilex FPGA Tx/Rx','RF & Transceivers','Agilex'),14:('phased-array-versal-processing','Phased-Array Versal FPGA','Radar & AI Processing','Versal'),15:('phased-array-agilex-processing','Phased-Array Agilex FPGA','Radar & AI Processing','Agilex'),17:('amd-radar-processor','AMD Processor','Radar & AI Processing','AMD'),18:('intel-radar-processor','Intel Processor','Radar & AI Processing','Intel')}
with ZipFile(source) as z:
 rows=list(csv.DictReader(io.StringIO(z.read('Product_Index.csv').decode('utf-8-sig'))))
 for row in rows:
  num=int(row['Product number']);code=row['Filename'];data=z.read(row['Datasheet']);pdf=fitz.open(stream=data,filetype='pdf');cover=pdf[0].get_text();desc=' '.join(cover.split('PRODUCT DESCRIPTION\n')[1].split('PRODUCT HIGHLIGHTS')[0].split())
  if num<=11:p=P[num-1]
  elif num==16:p=next(p for p in P if p['slug']=='nvidia-jetson-radar')
  else:
   slug,title,category,family=new[num];sub='Integrated antenna backplane system' if num in (12,13) else 'Radar signal & data processing system' if num in (14,15) else 'Radar processing system'
   image='/assets/products/'+slug+'.svg'
   (D/image.lstrip('/')).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="650" viewBox="0 0 1000 650"><rect width="1000" height="650" rx="24" fill="#f1f6f9"/><rect x="110" y="100" width="780" height="450" rx="20" fill="white" stroke="#dce6ec"/><text x="500" y="235" text-anchor="middle" font-family="Arial" font-size="24" fill="#608292">AVARTHANA</text><text x="500" y="335" text-anchor="middle" font-family="Arial" font-size="32" fill="#173b4b">'+escape(code)+' / '+escape(family)+'</text><text x="500" y="400" text-anchor="middle" font-family="Arial" font-size="22" fill="#608292">Product image on request</text></svg>')
   p=dict(id=max(x['id'] for x in P)+1,slug=slug,title=title,subtitle=sub,category=category,form='Antenna backplane' if num<16 else 'System',family=family,processor=family+' architecture; configuration-dependent',channels=None,summary=desc.split('. ')[0]+'.',description=[desc],highlights=['Configurable architecture: '+family+' processing selected for the application.','System integration: Interfaces, firmware and physical implementation are configuration-dependent.','Product documentation: Datasheet and separate block diagram provided for the selected platform.'],specs={'Configuration':[['Product reference',code],['Processing family',family],['Application',sub],['Detailed specifications','See the configurable product datasheet for interface, resource and integration targets.']]},notes=[],metrics=[['Reference',code],['Architecture',family],['Configuration','Selectable'],['Documentation','Rev 03']],image=image,diagram=None)
   P.append(p)
  p['document_code']=code;p['document_revision']='Rev 03 · 17 November 2026'
  p['datasheet']='/downloads/'+code+'.pdf';p['diagram_pdf']='/downloads/'+code+'_Block_Diagram.pdf';p['diagram']='/downloads/'+code+'_Block_Diagram.png';p['download_package']='/downloads/'+code+'_Documents.zip'
  for key,sourcekey in [('datasheet','Datasheet'),('diagram_pdf','Diagram PDF'),('diagram','Diagram PNG')]: (D/p[key].lstrip('/')).write_bytes(z.read(row[sourcekey]))
  with ZipFile(D/p['download_package'].lstrip('/'),'w',ZIP_DEFLATED) as pack:
   for key in ['datasheet','diagram_pdf','diagram']:pack.write(D/p[key].lstrip('/'),Path(p[key]).name)
   pack.writestr('Readme.txt',code+' | '+row['Product']+'\nRevision 03 | 17 November 2026\nSpecifications are configurable design targets. Released configuration and qualification status require confirmation.\n'+('Block diagram is conceptual; detailed reference drawings were not supplied.\n' if num in (17,18) else 'Reference diagrams can differ from the released implementation.\n'))
  p['document_sizes']={key:(D/p[key].lstrip('/')).stat().st_size for key in ['datasheet','diagram_pdf','download_package']}
  p['document_pages']={'datasheet':len(pdf),'diagram_pdf':len(fitz.open(D/p['diagram_pdf'].lstrip('/')))}
  p['notes']=[n for n in p['notes'] if 'configurable design targets' not in n]+['Revision 03 documentation contains configurable design targets; device resources, interfaces and completed qualification are confirmed for the released implementation.']
  if num in (17,18):p['notes'].append('The supplied block diagram is a conceptual architecture, not a detailed released hardware drawing.')
 # One up-to-date, deduplicated PDF containing all current product datasheets.
 merged=fitz.open()
 for p in P:
  with fitz.open(D/p['datasheet'].lstrip('/')) as doc:merged.insert_pdf(doc)
 merged.save(out/'avarthana-product-catalogue.pdf',garbage=4,deflate=True)
 (out/'Product_Index.csv').write_bytes(z.read('Product_Index.csv'))
(ROOT/'products.json').write_text(json.dumps(P,indent=2));(D/'assets/products.json').write_text(json.dumps(P,indent=2))
print('Imported',len(rows),'document sets;',len(P),'website products; catalogue MB',round((out/'avarthana-product-catalogue.pdf').stat().st_size/1024**2,1))
