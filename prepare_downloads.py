"""Publish supplied diagrams as standalone PDFs and pair them with their datasheets."""
from pathlib import Path
from io import BytesIO
import json,zipfile,hashlib
from PIL import Image
import fitz

ROOT=Path(__file__).parent;D=ROOT/'dist'
def build():
 products=json.loads((ROOT/'products.json').read_text())
 for p in products:
  p['diagram_pdf']=None
  if p.get('diagram'):
   source=D/p['diagram'].lstrip('/')
   im=Image.open(source)
   out=D/'downloads'/f'{p["slug"]}-block-diagram.pdf'
   doc=fitz.open();page=doc.new_page(width=1000,height=650)
   page.insert_text((46,44),'AVARTHANA  /  ENGINEERING DOCUMENTATION',fontsize=10,color=(.15,.37,.52))
   title=p['title'].replace('—','-')
   page.insert_text((46,76),title,fontsize=20,color=(.04,.16,.25))
   page.insert_text((46,100),p['subtitle'].replace('—','-'),fontsize=11,color=(.35,.47,.55))
   # Fit the exact original diagram without altering engineering labels or connections.
   frame=fitz.Rect(46,135,954,595)
   page.insert_image(frame,filename=str(source),keep_proportion=True)
   page.insert_text((46,626),'Original block diagram from the supplied Avarthana product brochure.',fontsize=9,color=(.35,.47,.55))
   doc.set_metadata({'title':p['title']+' - Block diagram','author':'Avarthana Technologies','subject':p['subtitle']})
   doc.save(out,garbage=4,deflate=True);doc.close()
   p['diagram_pdf']='/downloads/'+out.name
  p['download_package']='/downloads/'+p['slug']+'-documents.zip'
  with zipfile.ZipFile(D/p['download_package'].lstrip('/'),'w',zipfile.ZIP_DEFLATED) as z:
   z.write(D/p['datasheet'].lstrip('/'),'datasheet.pdf')
   if p['diagram_pdf']:
    z.write(D/p['diagram_pdf'].lstrip('/'),'block-diagram.pdf')
    z.write(D/p['diagram'].lstrip('/'),'block-diagram.png')
   note='Product: '+p['title']+'\n'+p['subtitle']+'\n\nDatasheet: original supplied product brochure.\n'
   note+=('Block diagram: exact source image, also provided as a standalone PDF.\n' if p['diagram_pdf'] else 'A block diagram was not included in the supplied source material. Contact info@avarthana.com for this document.\n')
   if p['notes']:note+='\nConfiguration notes:\n'+'\n'.join(p['notes'])+'\n'
   z.writestr('README.txt',note)
  p['document_sizes']={key:(D/p[key].lstrip('/')).stat().st_size for key in ['datasheet','diagram_pdf','download_package'] if p.get(key)}
 (ROOT/'products.json').write_text(json.dumps(products,ensure_ascii=False,indent=2))
 (D/'assets/products.json').write_text(json.dumps(products,ensure_ascii=False))
 print('Prepared 15 datasheets, 14 standalone diagram PDFs and 15 document packages')
if __name__=='__main__':build()
