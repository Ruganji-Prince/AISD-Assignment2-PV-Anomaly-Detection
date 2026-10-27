"""Compact report-width layouts derived only from frozen tabular evidence."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import *
COLORS=['#245b8a','#bd6428','#348261'];KEYS=['LR__F6','RF__E4','LightGBM__E4']
def generate(details,comparison):
 out=OUT/'figures';plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':9,'axes.labelsize':8,'xtick.labelsize':7.5,'ytick.labelsize':7.5,'axes.spines.top':False,'axes.spines.right':False})
 def save(fig,name):fig.tight_layout();fig.savefig(out/name,dpi=300,facecolor='white');plt.close(fig)
 ablation=pd.read_csv(ROOT/'phase2_implementation/stage2/evidence/sensor_ablation_validation.csv')
 configs=['F6','E5','E4','C3','C2','S4','S2'];fig,ax=plt.subplots(figsize=(7.3,2.4))
 for j,family in enumerate(['LR','RF','LightGBM']):
  rows=ablation[ablation.model==family].set_index('configuration').loc[configs];ax.plot(configs,rows.macro_f1,'o-',ms=4,color=COLORS[j],label=family)
 ax.axhline(.8,color='grey',ls='--',lw=.8);ax.set_ylim(0,1.04);ax.set_ylabel('Macro-F1');ax.set_xlabel('Predeclared configuration');ax.set_title('VALIDATION block 13 — fixed-setting sensor ablation');ax.legend(ncol=3,fontsize=7,loc='lower left');ax.grid(alpha=.2);save(fig,'validation_sensor_ablation.png')
 labels=['Normal','Short circuit','Degradation','Open circuit','Shade'];fig,axes=plt.subplots(1,3,figsize=(7.3,2.65))
 for ax,metric in zip(axes,['precision','recall','f1']):
  a=np.array([[details[k]['per_class'][str(c)][metric] for k in KEYS] for c in range(5)]);ax.imshow(a,cmap='Blues',vmin=0,vmax=1,aspect='auto');ax.set_title(metric.capitalize());ax.set_xticks(range(3),['LR F6','RF E4','LightGBM E4'],rotation=25,ha='right');ax.set_yticks(range(5),labels if ax is axes[0] else ['']*5)
  for i in range(5):
   for j in range(3):ax.text(j,i,f'{a[i,j]:.3f}',ha='center',va='center',fontsize=7.3,color='white' if a[i,j]>.6 else 'black')
 fig.suptitle('TEST — frozen five-class performance',fontsize=9);save(fig,'test_per_class_metrics.png')
 fig,axes=plt.subplots(1,2,figsize=(7.3,2.75));x=np.arange(3)
 for j,(label,col) in enumerate([('Recall','test_alert_recall'),('Precision','test_alert_precision'),('F1','test_alert_F1'),('AP','test_alert_AP')]):axes[0].bar(x+(j-1.5)*.18,comparison.loc[KEYS,col],.18,label=label)
 axes[0].set_xticks(x,['LR F6','RF E4','LGBM E4']);axes[0].set_ylim(0,1.32);axes[0].legend(ncol=2,fontsize=6.5,loc='upper right');axes[0].set_title('TEST hardware alerts')
 for j,(label,col) in enumerate([('Normal','test_normal_FPR'),('Shade','test_shade_FPR'),('Combined','test_combined_FPR')]):axes[1].bar(x+(j-1)*.24,100*comparison.loc[KEYS,col],.24,label=label)
 axes[1].set_xticks(x,['LR F6','RF E4','LGBM E4']);axes[1].set_ylabel('False-positive rate (%)');axes[1].set_ylim(0,1.5);axes[1].axhline(1,color='red',ls='--',lw=.8);axes[1].legend(ncol=1,fontsize=6.4,loc='upper right');axes[1].set_title('TEST FPR; 1% combined target')
 fig.suptitle('Thresholds frozen on VALIDATION block 14',fontsize=9);save(fig,'test_hardware_alerts.png')
 perm=pd.read_csv(ROOT/'phase2_implementation/stage3/evidence/physical_channel_permutation.csv');channels=['vdc1','vdc2','idc1','idc2','irr','pvt'];fig,ax=plt.subplots(figsize=(7.3,2.45));x=np.arange(6)
 for j,key in enumerate(KEYS):
  rows=perm[perm.candidate==key].groupby('channel').macro_f1_loss.agg(['mean','std']).reindex(channels);ax.bar(x+(j-1)*.24,rows['mean'],.24,yerr=rows['std'],label=key.replace('__',' '),color=COLORS[j],capsize=2)
 ax.set_xticks(x,channels);ax.set_ylabel('Macro-F1 decrease');ax.set_xlabel('Retained raw channel (E4 has no irr/pvt)');ax.set_ylim(0,.76);ax.legend(ncol=3,fontsize=7,loc='upper right');ax.set_title('VALIDATION block 13 — balanced N = 1,000; three permutations');save(fig,'validation_physical_channel_importance.png')
 shap=pd.read_csv(ROOT/'phase2_implementation/stage3/evidence/shap_mean_absolute.csv');r=shap[(shap['class']==1)&shap.feature.str.startswith('numeric__')].sort_values('mean_abs_SHAP');fig,ax=plt.subplots(figsize=(7.3,2.55));ax.barh(r.feature.str.replace('numeric__',''),r.mean_abs_SHAP,color=COLORS[2]);ax.set_xlabel('Mean |Tree SHAP| (short-circuit raw margin)');ax.set_title('VALIDATION block 13 — LightGBM E4; balanced N = 1,000');save(fig,'validation_lightgbm_short_circuit_shap.png')
 fig,ax=plt.subplots(figsize=(7.3,2.35));offsets=[(8,-26),(-100,14),(5,18)]
 for j,key in enumerate(KEYS):
  r=comparison.loc[key];ax.scatter(r.validation_p95_ms,r.test_macro_f1,s=70+220*r.artifact_MiB/12,color=COLORS[j]);ax.annotate(key.replace('__',' ')+f' · {int(r.physical_channels)} channels · {r.artifact_MiB:.4f} MiB',(r.validation_p95_ms,r.test_macro_f1),xytext=offsets[j],textcoords='offset points',fontsize=7.8)
 ax.axvline(10,color='red',ls='--',lw=.8);ax.axhline(.8,color='grey',ls=':',lw=.8);ax.set_xlim(0,43);ax.set_ylim(.78,1.03);ax.set_xlabel('VALIDATION block-13 single-observation p95 (ms)');ax.set_ylabel('TEST macro-F1');ax.set_title('TRAIN-fitted artifact size shown in labels and marker area');ax.grid(alpha=.2);save(fig,'performance_resource_tradeoff.png')
