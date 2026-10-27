"""Population-labeled final diagnostic figures, without model changes."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve,average_precision_score
from PIL import Image
from .common import *
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
LABELS=['Normal','Short circuit','Degradation','Open circuit','Building shade']
COLORS=['#245b8a','#bd6428','#348261']
INVENTORY=[]
def save(fig,name,population,description):
 fig.tight_layout();path=OUT/'figures'/name;fig.savefig(path,dpi=300,bbox_inches='tight');plt.close(fig)
 with Image.open(path) as im:width,height=im.size
 INVENTORY.append({'file':path.relative_to(ROOT).as_posix(),'population':population,'description':description,'width':width,'height':height,'dpi':300,'bytes':path.stat().st_size,'sha256':sha(path)})
def main():
 d=json.loads((E/'final_test_details.json').read_text())['results'];comp=pd.read_csv(E/'final_candidate_comparison.csv').set_index('candidate')
 for key in CANDIDATES:
  a=np.array(d[key]['confusion_matrix']);b=np.array(d[key]['row_normalized_confusion_matrix']);fig,axes=plt.subplots(1,2,figsize=(12,4.6))
  for ax,values,title in zip(axes,[a,b],['Counts','Row-normalized fraction']):
   im=ax.imshow(values,cmap='Blues',vmin=0,vmax=None if title=='Counts' else 1,aspect='auto');fig.colorbar(im,ax=ax,fraction=.04)
   ax.set_xticks(range(6),LABELS+['Abstain'],rotation=40,ha='right');ax.set_yticks(range(5),LABELS);ax.set_xlabel('Predicted state');ax.set_ylabel('True state');ax.set_title(title)
   for i in range(5):
    for j in range(6):ax.text(j,i,str(int(values[i,j])) if title=='Counts' else f'{values[i,j]:.3f}',ha='center',va='center',fontsize=8,color='white' if values[i,j]>values.max()*.6 else 'black')
  fig.suptitle(f'TEST — {key.replace("__"," ")} — fixed final evaluation',y=1.02)
  save(fig,'test_confusion_'+key+'.png','TEST','Five-class confusion with separate abstention column; counts and row normalization.')
 fig,axes=plt.subplots(1,3,figsize=(14,4.5));x=np.arange(5)
 for ax,metric in zip(axes,['precision','recall','f1']):
  for j,key in enumerate(CANDIDATES):ax.bar(x+(j-1)*.24,[d[key]['per_class'][str(k)][metric] for k in range(5)],.24,label=key.replace('__',' '),color=COLORS[j])
  ax.set_xticks(x,LABELS,rotation=35,ha='right');ax.set_ylim(0,1.08);ax.set_title(metric.capitalize());ax.grid(axis='y',alpha=.2)
 axes[0].legend(fontsize=8);fig.suptitle('TEST — per-class classification metrics',y=1.02);save(fig,'test_per_class_metrics.png','TEST','Classification precision, recall and F1; shade is environmental.')
 fig,axes=plt.subplots(1,2,figsize=(12,4.8));x=np.arange(3)
 for j,(name,col) in enumerate([('Recall','test_alert_recall'),('Precision','test_alert_precision'),('F1','test_alert_F1'),('Average precision','test_alert_AP')]):axes[0].bar(x+(j-1.5)*.18,comp.loc[CANDIDATES,col],.18,label=name)
 axes[0].set_xticks(x,[k.replace('__','\n') for k in CANDIDATES]);axes[0].set_ylim(0,1.08);axes[0].legend(fontsize=8,loc='lower center',bbox_to_anchor=(.5,-.30),ncol=2);axes[0].set_title('Hardware alert performance')
 for j,(name,col) in enumerate([('Normal FPR','test_normal_FPR'),('Shade FPR','test_shade_FPR'),('Combined FPR','test_combined_FPR')]):axes[1].bar(x+(j-1)*.24,100*comp.loc[CANDIDATES,col],.24,label=name)
 axes[1].axhline(1,color='red',ls='--',label='1% combined-FPR target');axes[1].set_ylabel('False-positive rate (%)');axes[1].set_xticks(x,[k.replace('__','\n') for k in CANDIDATES]);axes[1].legend(fontsize=8);axes[1].set_title('Separate populations; target applies to combined FPR')
 fig.suptitle('TEST — hardware alert thresholds frozen on VALIDATION block 14',y=1.02);save(fig,'test_hardware_alerts.png','TEST; thresholds from VALIDATION block14','Thresholded hardware alert results, separate from argmax class recall.')
 fig,axes=plt.subplots(2,3,figsize=(14,8))
 for ax,k in zip(axes.ravel(),range(6)):
  for j,key in enumerate(CANDIDATES):
   z=np.load(ROOT/'.cache/stage3'/(key+'_test.npz'));p=np.nan_to_num(z['p'],nan=0.);y=z['y'];truth=np.isin(y,[1,2,3]) if k==5 else y==k;score=p[:,1:4].sum(1) if k==5 else p[:,k]
   precision,recall,_=precision_recall_curve(truth,score);ap=average_precision_score(truth,score);ax.plot(recall,precision,color=COLORS[j],label=key.replace('__',' ')+f' AP={ap:.3f}')
  ax.set_title(LABELS[k] if k<5 else 'Hardware aggregate {1,2,3}');ax.set_xlabel('Recall');ax.set_ylabel('Precision');ax.set_xlim(0,1.01);ax.set_ylim(0,1.03);ax.legend(fontsize=7);ax.grid(alpha=.2)
 fig.suptitle('TEST — one-vs-rest precision–recall; AP is average precision',y=1.01);save(fig,'test_precision_recall.png','TEST','Five class PR curves and hardware aggregate; full test prevalence retained.')
 rows=pd.read_csv(ROOT/'phase2_implementation/stage2/evidence/sensor_ablation_validation.csv');fig,axes=plt.subplots(1,3,figsize=(13,4.5))
 for ax,f in zip(axes,['LR','RF','LightGBM']):
  r=rows[rows.model==f];ax.bar(r.configuration,r.macro_f1,color=COLORS[['LR','RF','LightGBM'].index(f)]);ax.axhline(.8,color='red',ls='--',lw=1);ax.set_ylim(0,1.04);ax.set_title(f);ax.set_ylabel('Macro-F1');ax.set_xlabel('Predeclared sensor configuration')
 fig.suptitle('VALIDATION block 13 — frozen Stage 2 ablation (no new selection)',y=1.02);save(fig,'validation_sensor_ablation.png','VALIDATION block13','Frozen 21-run Stage 2 ablation reproduced directly from approved CSV.')
 fig,axes=plt.subplots(1,3,figsize=(13,4.3))
 for ax,col,xlabel in zip(axes,['physical_channels','validation_p95_ms','artifact_MiB'],['Physical channels','VALIDATION block-13 single-row p95 (ms)','Serialized complete artifact (MiB)']):
  for j,key in enumerate(CANDIDATES):
   r=comp.loc[key];ax.scatter(r[col],r.test_macro_f1,s=70+25*r.physical_channels,color=COLORS[j],label=key.replace('__',' '))
  ax.axhline(.8,color='grey',ls=':',lw=1);ax.set_ylim(.78,1.01);ax.set_xlabel(xlabel);ax.set_ylabel('TEST macro-F1');ax.grid(alpha=.2)
  if col=='validation_p95_ms':ax.axvline(10,color='red',ls='--',lw=1)
  if col=='artifact_MiB':ax.axvline(10,color='red',ls='--',lw=1)
 axes[0].set_xlim(3,7);axes[0].legend(fontsize=8);fig.suptitle('Frozen candidates — TEST performance; VALIDATION timing; fitted-artifact size',y=1.02);save(fig,'performance_resource_tradeoff.png','TEST macro-F1; VALIDATION block13 timing; TRAIN-fitted artifacts','Marker area represents physical-channel count; populations explicitly separated.')
 perm=pd.read_csv(E/'physical_channel_permutation.csv');fig,axes=plt.subplots(1,3,figsize=(13,4.3))
 for ax,key in zip(axes,CANDIDATES):
  r=perm[perm.candidate==key].groupby('channel').macro_f1_loss.agg(['mean','std']).sort_values('mean');ax.barh(r.index,r['mean'],xerr=r['std'],color=COLORS[CANDIDATES.index(key)]);ax.axvline(0,color='grey',lw=1);ax.set_xlabel('Macro-F1 decrease (3 permutations)');ax.set_title(key.replace('__',' '))
 fig.suptitle('VALIDATION block 13 — raw physical-channel permutation; balanced N=1,000',y=1.02);save(fig,'validation_physical_channel_importance.png','VALIDATION block13 class-balanced sample','Raw-channel permutation regenerates all deterministic derivatives; association, not causation.')
 native=pd.read_csv(E/'native_feature_importance.csv');fig,axes=plt.subplots(1,3,figsize=(14,5.5))
 for ax,key in zip(axes,CANDIDATES):
  r=native[native.candidate==key].sort_values('importance');ax.barh(r.feature.str.replace('numeric__','').str.replace('missing__',''),r.importance,color=COLORS[CANDIDATES.index(key)]);ax.set_title(key.replace('__',' '));ax.set_xlabel('Mean |coefficient|' if key.startswith('LR') else ('Impurity importance' if key.startswith('RF') else 'Split gain'))
 fig.suptitle('TRAIN-fitted model feature importance — method-specific, not comparable scales',y=1.02);save(fig,'train_native_feature_importance.png','TRAIN fitted coefficients/impurity/gain','Mathematical features and availability indicators; not independent sensors.')
 shap=pd.read_csv(E/'shap_mean_absolute.csv');fig,axes=plt.subplots(1,3,figsize=(15,5))
 for ax,k in zip(axes,[1,2,3]):
  r=shap[shap['class']==k].sort_values('mean_abs_SHAP');ax.barh(r.feature.str.replace('numeric__','').str.replace('missing__',''),r.mean_abs_SHAP,color=COLORS[k-1]);ax.set_title(LABELS[k]);ax.set_xlabel('Mean |Tree SHAP| (raw class margin)')
 fig.suptitle('VALIDATION block 13 — LightGBM E4 Tree SHAP; balanced N=1,000',y=1.02);save(fig,'validation_lightgbm_class_shap.png','VALIDATION block13 class-balanced sample','Class-specific Tree SHAP mathematical-feature contribution; additive raw margin verified.')
 write_json(E/'figure_inventory.json',INVENTORY)
 print('Generated',len(INVENTORY),'population-labeled 300-DPI figures',flush=True)
if __name__=='__main__':main()
