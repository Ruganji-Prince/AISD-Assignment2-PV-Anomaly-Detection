"""Render presentation assets from completed CSVs only; no model execution."""
from pathlib import Path
import hashlib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;FIG=OUT/'figures'
FIG.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
csv_hashes={p.name:sha(p) for p in OUT.glob('*.csv')}
s=pd.read_csv(OUT/'Noise_Robustness_Summary.csv');plot=pd.read_csv(OUT/'Noise_Plot_Data_Verification.csv')
keys=['RF__E4','LightGBM__E4'];levels=[0,.01,.02,.05,.1];colors=['#246a9b','#d47a20']
names=['Reconstructed RF E4','Reconstructed LightGBM E4'];short=['RF E4','LightGBM E4']
def row(k,a):return s[(s.model==k)&(s.alpha==a)].iloc[0]
def value(r,metric,factor=1):
    m=r[metric+'_mean']*factor;sd=r[metric+'_std']*factor
    return f'{m:.4f}' if r.alpha==0 else f'{m:.4f} ± {sd:.4f}'
coverage={a:value(row(keys[0],a),'coverage',100)+'%' for a in levels}
expected=['100.0000%','92.1941 ± 0.0737%','84.4133 ± 0.0997%','74.7809 ± 0.1046%','69.5123 ± 0.1124%']
assert list(coverage.values())==expected
for a in levels:
    assert row(keys[0],a).coverage_mean==row(keys[1],a).coverage_mean
    assert row(keys[0],a).coverage_std==row(keys[1],a).coverage_std
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
terminology='End-to-end pipeline robustness under Gaussian sensor noise,\nincluding existing input-quality/abstention rules.'
quality='Coverage decreases because the unchanged input-quality rules can convert noise-induced negative electrical readings\nto missing values and trigger abstention.'
def save(fig,stem):
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    for text in fig.texts:
        b=text.get_window_extent(renderer)
        assert b.x0>=0 and b.x1<=fig.bbox.width and b.y0>=0 and b.y1<=fig.bbox.height,(stem,text.get_text())
    fig.savefig(FIG/(stem+'.png'),dpi=320,bbox_inches='tight',facecolor='white')
    fig.savefig(FIG/(stem+'.pdf'),bbox_inches='tight',facecolor='white');plt.close(fig)
series=[('macro_f1','noise_macro_f1','Macro-F1',False,False),('hardware_macro_recall','noise_hardware_macro_recall','Hardware macro recall',True,False),('class1_recall','noise_short_circuit_recall','Short-circuit classification recall',True,False),('combined_FPR','noise_combined_fpr','Combined hardware-alert FPR (%)',False,True)]
for metric,stem,label,reference,percent in series:
    fig,ax=plt.subplots(figsize=(12,8.5));factor=100 if percent else 1
    for key,name,color in zip(keys,names,colors):
        g=s[s.model==key].sort_values('alpha');x=g.alpha.to_numpy()*100;yy=g[metric+'_mean'].to_numpy()*factor;err=g[metric+'_std'].to_numpy()*factor
        old=plot[(plot.figure==stem)&(plot.model==key)].sort_values('alpha')
        np.testing.assert_allclose(yy,old.mean_plotted,rtol=0,atol=1e-14);np.testing.assert_allclose(err,old.sample_SD_plotted,rtol=0,atol=1e-14)
        ax.errorbar(x,yy,yerr=err,marker='o',lw=2,capsize=4,color=color,label=name)
    if reference:ax.axhline(.9,color='#8d2a2a',ls='--',lw=1.3,label='0.90 reference: original per-hardware-class target')
    ax.set_xticks([0,1,2,5,10],['0%','1%','2%','5%','10%']);ax.set_xlabel('Noise SD as a fraction of each channel’s TRAIN SD');ax.set_ylabel(label)
    ax.set_title('Additional Post-Hoc Noise Robustness Analysis\n'+label,pad=14)
    ax.grid(alpha=.2);ax.legend(fontsize=9,loc='best');ax.set_axisbelow(True)
    ax.set_ylim(0,1.03) if not percent else ax.set_ylim(bottom=0)
    fig.subplots_adjust(left=.10,right=.98,top=.87,bottom=.37)
    cnote='Coverage (both models): clean '+coverage[0]+'; 1% '+coverage[.01]+'; 2% '+coverage[.02]+';\n5% '+coverage[.05]+'; 10% '+coverage[.1]+'.'
    fig.text(.54,.255,cnote,ha='center',va='center',fontsize=10.5,linespacing=1.5,color='#183f59',weight='bold')
    fig.text(.54,.185,'Mean ± sample SD across 10 paired seeds at nonzero noise; clean n=1. Coverage is shared by both models.',ha='center',fontsize=9.5)
    fig.text(.54,.125,quality,ha='center',va='center',fontsize=10,linespacing=1.4)
    fig.text(.54,.047,terminology,ha='center',va='center',fontsize=10,linespacing=1.4)
    save(fig,stem)
hardware=[];overall=[];alert=[]
for a in levels:
    noise='Clean' if a==0 else f'{a*100:.0f}%'
    for k,name in zip(keys,short):
        r=row(k,a)
        hardware.append([noise,coverage[a],name,*[value(r,c) for c in ['class1_recall','class2_recall','class3_recall','hardware_macro_recall']]])
        alert.append([noise,coverage[a],name,value(r,'alert_recall'),value(r,'alert_f1'),value(r,'combined_FPR',100)+'%'])
    rf=row(keys[0],a);lg=row(keys[1],a)
    overall.append([noise,coverage[a],value(rf,'macro_f1'),value(lg,'macro_f1'),value(rf,'hardware_macro_recall'),value(lg,'hardware_macro_recall')])
tables=[('noise_hardware_recall_table','Hardware-class recall under sensor measurement noise',['Noise','Coverage','Model','Short recall','Degradation recall','Open recall','HW macro recall'],hardware,[.055,.19,.105,.16,.165,.16,.165]),('noise_overall_table','Overall classification under sensor measurement noise',['Noise','Coverage','RF Macro-F1','LightGBM\nMacro-F1','RF HW\nmacro recall','LightGBM HW\nmacro recall'],overall,[.05,.19,.19,.19,.19,.19]),('noise_alert_table','Hardware alerts at the original frozen thresholds',['Noise','Coverage','Model','Alert recall','Alert F1','Combined FPR'],alert,[.06,.21,.12,.19,.19,.23])]
for stem,title,headers,rows,widths in tables:
    fig,ax=plt.subplots(figsize=(22,10 if len(rows)>5 else 8));ax.axis('off')
    tab=ax.table(cellText=rows,colLabels=headers,cellLoc='center',colWidths=widths,bbox=[.015,.32,.97,.58]);tab.auto_set_font_size(False)
    for (r,c),cell in tab.get_celld().items():
        cell.set_edgecolor('#dce4ea');cell.set_linewidth(.6);cell.set_text_props(fontsize=15 if len(headers)==7 else 17)
        if r==0:cell.set_facecolor('#183f59');cell.set_text_props(color='white',weight='bold')
        else:cell.set_facecolor('#f0f4f7' if ((r-1)//2 if len(rows)>5 else r-1)%2==0 else 'white')
    ax.set_title('Additional Post-Hoc Noise Robustness Analysis\n'+title,fontsize=22,pad=16,weight='bold')
    fig.text(.5,.245,'Coverage is identical for RF and LightGBM; one shared column. Noisy values: mean ± sample SD across 10 paired seeds.',ha='center',fontsize=13)
    fig.text(.5,.175,quality,ha='center',va='center',fontsize=13,linespacing=1.4)
    fig.text(.5,.075,terminology,ha='center',va='center',fontsize=13,linespacing=1.4)
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    for cell in tab.get_celld().values():
        text=cell.get_text().get_window_extent(renderer);box=cell.get_window_extent(renderer)
        assert box.x0<=text.x0 and text.x1<=box.x1 and box.y0<=text.y0 and text.y1<=box.y1,(stem,cell.get_text().get_text())
    save(fig,stem)
def mdtable(headers,rows):return '\n'.join(['| '+' | '.join(h.replace('\n',' ') for h in headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])
(OUT/'Noise_Presentation_Tables.md').write_text('\n\n'.join('## '+title+'\n\n'+mdtable(headers,rows)+'\n\n'+quality.replace('\n',' ')+'\n\n'+terminology.replace('\n',' ') for _,title,headers,rows,_ in tables),encoding='utf8')

assert all(sha(OUT/n)==h for n,h in csv_hashes.items())
print('Rendered seven presentation assets with shared coverage; CSVs unchanged.')
