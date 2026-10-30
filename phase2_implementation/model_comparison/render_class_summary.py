"""Presentation-only rendering of the published frozen comparison CSV."""
from pathlib import Path
import csv,hashlib,subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pymupdf

ROOT=Path(__file__).resolve().parents[2]
PKG=ROOT/'phase2_implementation/model_comparison'
CSV=PKG/'RF_vs_LightGBM_Class_Metrics.csv'
assert hashlib.sha256(CSV.read_bytes()).hexdigest()=='5ec2e3c016b32acb48f6aaec6e309ea428db56a5eab8de2fbc924d38df403560'
existing=list(PKG.rglob('*'))+list((ROOT/'phase2_implementation/reports').glob('*'))+[ROOT/'phase2_implementation/Phase2_Final_Report.pdf']
before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in existing if p.is_file() and not p.name.startswith('rf_vs_lgbm_class_summary_table')}
with CSV.open(newline='',encoding='utf8') as f:data={(int(r['class']),r['model']):r for r in csv.DictReader(f)}
names=['Normal','Short Circuit','Resistive\nDegradation','Open Circuit','Building Shade']
interpretations=['LightGBM','RF','RF overall','Essentially tied','LightGBM']
expected=[['0.9468','0.9725','0.9965','0.9982'],['0.9996','0.9821','0.4994','0.6561'],['0.9907','0.9845','0.9930','0.8980'],['1.0000','0.9990','0.9992','0.9990'],['0.9911','0.8144','0.9937','0.9594']]
rows=[]
for c in range(5):
    values=[f"{float(data[c,m][metric]):.4f}" for m in ['RF E4','LightGBM E4'] for metric in ['recall','f1']]
    assert values==expected[c]
    rows.append([names[c],*values,interpretations[c]])
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42,'ps.fonttype':42})
fig=plt.figure(figsize=(20,9),facecolor='white');ax=fig.add_axes([0,0,1,1]);ax.axis('off')
title=fig.text(.5,.925,'RF E4 vs LightGBM E4: Class-Level Performance',ha='center',va='center',fontsize=28,fontweight='bold',color='#18354b')
headers=['Class','RF E4\nRecall','RF E4\nF1','LightGBM E4\nRecall','LightGBM E4\nF1','Better overall /\ninterpretation']
t=ax.table(cellText=rows,colLabels=headers,cellLoc='center',colLoc='center',colWidths=[.20,.13,.12,.15,.14,.26],bbox=[.025,.245,.95,.60])
t.auto_set_font_size(False)
for (r,c),cell in t.get_celld().items():
    cell.set_edgecolor('#d9e2e9');cell.set_linewidth(.8);cell.PAD=.06
    if r==0:
        cell.set_facecolor('#183f59');cell.set_text_props(color='white',fontweight='bold',fontsize=18)
    else:
        cell.set_facecolor('#f0f4f7' if r%2==1 else 'white');cell.set_text_props(fontsize=21,color='#243746')
        if c==0:cell.set_text_props(ha='left',fontsize=20)
        if c==5:cell.set_text_props(fontsize=20,fontweight='bold')
# Emphasize the stronger value separately for recall and F1. Do not exaggerate
# negligible open-circuit differences; the two displayed F1 values are tied.
for c in range(5):
    if c==3:continue
    for metric,rfcol,lgbcol in [('recall',1,3),('f1',2,4)]:
        rf=float(data[c,'RF E4'][metric]);lgb=float(data[c,'LightGBM E4'][metric])
        t[c+1,rfcol if rf>lgb else lgbcol].set_text_props(fontweight='bold',color='#075f84')
takeaway=('RF E4 is stronger for hardware fault-type identification, especially Short Circuit, while LightGBM E4\n'
          'performs better on Normal and Building Shade and is substantially more resource-efficient.')
foot=fig.text(.5,.12,takeaway,ha='center',va='center',fontsize=19,color='#243746',linespacing=1.55)
fig.canvas.draw();renderer=fig.canvas.get_renderer()
for text in [title,foot]+[cell.get_text() for cell in t.get_celld().values()]:
    box=text.get_window_extent(renderer)
    assert fig.bbox.contains(box.x0,box.y0) and fig.bbox.contains(box.x1,box.y1),'Figure text clips'
for cell in t.get_celld().values():
    box=cell.get_text().get_window_extent(renderer);bounds=cell.get_window_extent(renderer)
    assert bounds.x0<=box.x0 and box.x1<=bounds.x1 and bounds.y0<=box.y0 and box.y1<=bounds.y1,'Cell text clips'
stem=PKG/'figures/rf_vs_lgbm_class_summary_table'
fig.savefig(stem.with_suffix('.png'),dpi=400,facecolor='white')
fig.savefig(stem.with_suffix('.pdf'),facecolor='white',metadata={'Title':'RF E4 vs LightGBM E4: Class-Level Performance','Subject':'Frozen five-class recall and F1 summary'})
plt.close(fig)
doc=pymupdf.open(stem.with_suffix('.pdf'));assert len(doc)==1
text=doc[0].get_text()
for vals in expected:
    for val in vals:assert val in text
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in before.items())
print('PASS: published CSV byte match; all 20 displayed values verified; cell/figure bounds checked; existing files unchanged.')
print('PNG: 8000 x 3600 pixels, 400 dpi; PDF: vector text, one landscape page.')
print(stem.with_suffix('.png'));print(stem.with_suffix('.pdf'))
