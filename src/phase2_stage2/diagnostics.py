"""Six compact validation-block-13 ablation/resource plots; ordinary scientific styling."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from .contracts import *


def _save(fig,name):
 dest=OUT/'figures';dest.mkdir(exist_ok=True);fig.tight_layout();fig.savefig(dest/name,dpi=300,facecolor='white');plt.close(fig)


def generate(table):
 colors={'LR':'#1f77b4','RF':'#d95f02','LightGBM':'#2ca02c'}
 for metric,label,name,line in [('macro_f1','Macro-F1','validation_macro_f1_vs_channels.png',.80),
  ('hardware_macro_recall','Hardware macro recall','validation_hardware_recall_vs_channels.png',.90),
  ('delta_s','Same-family macro-F1 degradation','validation_delta_vs_channels.png',.05)]:
  fig,axes=plt.subplots(1,3,figsize=(12,3.8),sharey=True)
  for ax,family in zip(axes,FAMILIES):
   group=table[table.model==family]
   ax.scatter(group.physical_channels,group[metric],color=colors[family])
   for i,(_,row) in enumerate(group.iterrows()):ax.annotate(row.configuration,(row.physical_channels,row[metric]),xytext={'F6':(6,12),'E5':(-18,12),'E4':(6,-15),'C3':(6,-15),'C2':(6,12),'S4':(6,-15),'S2':(6,-15)}[row.configuration],textcoords='offset points',fontsize=8)
   ax.axhline(line,color='gray',linestyle='--',linewidth=.8);ax.set(title=family,xlabel='Physical channels',xticks=[2,3,4,5,6]);ax.grid(alpha=.2);ax.margins(x=.15,y=.15)
  axes[0].set_ylabel(label);fig.suptitle('Validation block 13 only');_save(fig,name)
 for metric,label,name in [('macro_f1','Macro-F1','validation_macro_f1_heatmap.png'),('hardware_macro_recall','Hardware macro recall','validation_hardware_recall_heatmap.png')]:
  a=np.array([[float(table[(table.model==f)&(table.configuration==c)][metric].iloc[0]) for c in CONFIGS] for f in FAMILIES])
  fig,ax=plt.subplots(figsize=(9,3.8));im=ax.imshow(a,vmin=0,vmax=1,cmap='viridis',aspect='auto')
  for i in range(3):
   for j in range(7):ax.text(j,i,f'{a[i,j]:.3f}',ha='center',va='center',color='white' if a[i,j]<.65 else 'black',fontsize=9)
  ax.set(xticks=range(7),xticklabels=list(CONFIGS),yticks=range(3),yticklabels=FAMILIES,title='Validation block 13: '+label);fig.colorbar(im,ax=ax);_save(fig,name)
 fig,axes=plt.subplots(2,3,figsize=(13,8),sharey=True)
 offsets={'F6':(6,12),'E5':(-18,12),'E4':(6,-15),'C3':(6,-15),'C2':(6,12),'S4':(6,-15),'S2':(6,-15)}
 for j,family in enumerate(FAMILIES):
  group=table[table.model==family]
  for i,(resource,xlabel,unit) in enumerate([('artifact_MiB','Complete pipeline artifact (MiB)','MiB'),('p95_ms','Single-observation p95 (ms)','ms')]):
   ax=axes[i,j];ax.scatter(group[resource],group.macro_f1,s=20+group.physical_channels*12,color=colors[family],alpha=.8)
   for _,row in group.iterrows():
    offset=offsets[row.configuration]
    if resource=='artifact_MiB' and family=='RF':offset={'F6':(6,-18),'E5':(-24,15),'E4':(16,0)}.get(row.configuration,offset)
    if resource=='artifact_MiB' and family=='LightGBM':offset={'F6':(-25,8),'E5':(12,20),'E4':(5,-18),'S4':(-25,10),'S2':(8,-16)}.get(row.configuration,offset)
    ax.annotate(row.configuration,(row[resource],row.macro_f1),fontsize=8,xytext=offset,textcoords='offset points',arrowprops={'arrowstyle':'-','color':'gray','lw':.4})
   lo=float(group[resource].min());hi=float(group[resource].max());pad=max((hi-lo)*.25,hi*.05)
   ax.set_xlim(lo-pad,hi+pad);ax.set_ylim(.08,1.04)
   note='all <= 10 '+unit if hi<=10 else ('all > 10 '+unit if lo>10 else 'target <= 10 '+unit)
   if lo-pad<=10<=hi+pad:ax.axvline(10,color='gray',linestyle='--',linewidth=.8)
   ax.axhline(.8,color='gray',linestyle='--',linewidth=.8);ax.set(title=family+'; '+note,xlabel=xlabel);ax.grid(alpha=.2)
 axes[0,0].set_ylabel('Validation macro-F1');axes[1,0].set_ylabel('Validation macro-F1')
 fig.suptitle('Validation block 13 resource trade-offs; marker area encodes physical channel count')
 _save(fig,'validation_resource_tradeoffs.png')
