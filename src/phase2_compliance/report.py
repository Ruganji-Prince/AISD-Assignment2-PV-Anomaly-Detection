"""Append the assignment reflection table; preserve all ten original scientific pages."""
import html,json
import pymupdf as pdf
from .common import *
from .strategy import ROWS

def main():
 report=ROOT/'phase2_implementation/reports/Phase2_Final_Report.pdf';doc=pdf.open(report)
 assert len(doc)>=10
 # Rebuild only the compliance appendix. The ten original page objects are copied unchanged.
 result=pdf.open();result.insert_pdf(doc,from_page=0,to_page=9);doc.close()
 css='body{font-family:serif;font-size:9.3pt;color:#151515;}h2{font-size:12pt;margin:0 0 7pt;}p{margin:5pt 0 7pt;}table{border-collapse:collapse;width:100%;font-size:8pt;}th,td{border:.4pt solid #777;padding:3.5pt;vertical-align:top;}th{background-color:#f0f0f0;}.note{font-size:8pt;}'
 counts=[]
 for part,rows in enumerate([ROWS[:11],ROWS[11:]],1):
  page=result.new_page(width=612,height=792)
  title='Appendix A. Strategy versus reality'+(' — continued' if part==2 else '')
  intro='The original ten pages retain the frozen experimental findings. This appendix records implementation choices and explicitly identifies the later compliance-only diagnostics. No model, sensor, threshold, split or final metric changed.' if part==1 else 'Table 9 continued. TRAIN-only MI/PCA diagnostics complete assignment coverage after the final model decisions were frozen; these statistics did not select another model or sensor set.'
  headers=['Phase 1 planned decision','Actual Phase 2 / compliance implementation','Status','Deviation / finding','Rationale / evidence']
  table='<table><tr>'+''.join('<th>'+h+'</th>' for h in headers)+'</tr>'
  for category,plan,actual,status,deviation,evidence in rows:
   values=[category+': '+plan,actual,status,deviation,evidence]
   table+='<tr>'+''.join('<td>'+html.escape(v)+'</td>' for v in values)+'</tr>'
  table+='</table>'
  content='<h2>'+title+'</h2><p>'+intro+'</p><p><b>Table 9'+(' (continued)' if part==2 else '')+'. Phase 1 plan, implementation and evidence</b></p>'+table
  spare,scale=page.insert_htmlbox(pdf.Rect(36,43,576,746),content,css=css,scale_low=1)
  if spare<0:raise RuntimeError('Appendix overflow; adjust presentation without changing scientific content.')
  page.insert_text((36,28),'PV Anomaly Detection | Assignment-compliance reflection',fontname='tiro',fontsize=8);page.insert_text((297,770),str(10+part),fontname='tiro',fontsize=9);counts.append({'page':10+part,'rows':len(rows),'scale':scale,'spare_height_pt':spare})
 result.set_metadata({'title':'AISD Assignment 2 — Phase 2: PV Anomaly Detection','author':'Ruganji Prince','subject':'Frozen scientific report with assignment-compliance reflection appendix'})
 data=result.tobytes(garbage=4,deflate=True);result.close()
 protection=load('phase2_implementation/compliance/Approved_Science_Protection.json');updated=pdf.open(stream=data,filetype='pdf');render_hash=[]
 import hashlib
 for i in range(10):
  after=updated[i].get_pixmap(matrix=pdf.Matrix(1,1)).samples;expected=protection['original_report_pages'][i]
  assert hashlib.sha256(after).hexdigest()==expected['render_sha256'],('Original report rendering changed',i+1)
  assert hashlib.sha256(updated[i].get_text().encode()).hexdigest()==expected['text_sha256'],('Original report text changed',i+1)
  render_hash.append(expected['render_sha256'])
 report.write_bytes(data)
 source=ROOT/'phase2_implementation/reports/Phase2_Final_Report.md';text=source.read_text(encoding='utf8').split('\n\n## Appendix A. Strategy versus reality')[0]
 appendix=(OUT/'Strategy_vs_Reality.md').read_text(encoding='utf8').replace('# Strategy versus reality','## Appendix A. Strategy versus reality',1)
 source.write_text(text.rstrip()+'\n\n'+appendix+'\n',encoding='utf8')
 write(OUT/'Report_Compliance_Addition.json',{'old_report_sha256':protection['original_report_sha256'],'new_report_sha256':sha(report),'pages':len(updated),'original_pages_unchanged_text_and_rendering':True,'original_page_render_sha256':render_hash,'new_table_number':9,'strategy_categories':len(ROWS),'appendix_layout':counts,'scientific_numbers_changed':False})
 print('Report:',len(updated),'pages; original ten pages identical in text/rendering; table9 appendix added.');print('Appendix layout:',counts)
if __name__=='__main__':main()
