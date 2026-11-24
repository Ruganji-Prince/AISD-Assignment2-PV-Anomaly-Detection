"""Figures computed only from saved machine-readable evidence."""
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve
from .common import *
def main():
 folder=OUT/'figures';folder.mkdir(exist_ok=True);plt.rcParams.update({'font.size':9,'figure.dpi':150})
 def save(name):plt.tight_layout();plt.savefig(folder/(name+'.png'),dpi=180,bbox_inches='tight',facecolor='white');plt.close()
 a=pd.read_csv(OUT/'evidence/rubric1/Pearson.csv',index_col=0);plt.figure(figsize=(6,5));plt.imshow(a,vmin=-1,vmax=1,cmap='RdBu_r');plt.colorbar(label='TRAIN Pearson r');plt.xticks(range(6),a.columns,rotation=45);plt.yticks(range(6),a.columns)
 for i in range(6):
  for j in range(6):plt.text(j,i,f'{a.iloc[i,j]:.2f}',ha='center',va='center',color='black' if abs(a.iloc[i,j])<.6 else 'white')
 save('TRAIN_correlation')
 x=load('evidence/rubric1/feature_screening.json');fig,ax=plt.subplots(1,2,figsize=(9,3));ax[0].bar(x['VIF'].keys(),x['VIF'].values());ax[0].axhline(10,color='red',linestyle='--');ax[0].set_yscale('log');ax[0].set_ylabel('TRAIN VIF');ax[0].tick_params(axis='x',rotation=45);ax[1].plot(np.arange(1,7),x['PCA_cumulative'],marker='o');ax[1].set(xlabel='Mathematical components (all six inputs)',ylabel='Cumulative TRAIN variance',ylim=(0,1.02));save('TRAIN_VIF_PCA')
 methods=load('evidence/rubric3/calibration_TEST_retrospective.json')['methods'];fig,axes=plt.subplots(2,3,figsize=(12,7))
 for name,item in methods.items():
  q=item['probability_quality']
  for k,ax in enumerate(axes.flat):
   rel=q['class_reliability'][str(k)] if k<5 else q['hardware_reliability'];bins=[r for r in rel['bins'] if r['N']];ax.plot([r['mean_probability'] for r in bins],[r['observed_frequency'] for r in bins],marker='.',label=name);ax.set(title='Class '+str(k) if k<5 else 'Hardware score',xlabel='Mean predicted probability',ylabel='Observed frequency');ax.plot([0,1],[0,1],':',color='gray')
 axes.flat[0].legend();fig.suptitle('Historical TEST reliability: retrospective, no pristine-test claim');save('calibration_reliability_TEST')
 select=load('evidence/rubric3/calibration_selection_freeze.json')['OOF_probability_quality'];fig,axes=plt.subplots(1,3,figsize=(10,3))
 for ax,key in zip(axes,['multiclass_Brier','log_loss','ECE']):
  ax.bar(select.keys(),[v['top_label_reliability']['ECE'] if key=='ECE' else v[key] for v in select.values()]);ax.set_title('Block14 cross-fitted '+key);ax.tick_params(axis='x',rotation=30)
 save('calibration_selection_OOF')
 d=raw()
 for partname in ['VALIDATION','TEST']:
  f=part(d,partname);p=np.load(CACHE/(partname+'_probabilities.npz'))['p'];fig,ax=plt.subplots(figsize=(6,4))
  for k in range(5):pr,re,_=precision_recall_curve(f.f_nv==k,p[:,k]);ax.plot(re,pr,label='Class'+str(k))
  ax.set(xlabel='Recall',ylabel='Precision',title=partname+' original RF E4 (AP is not trapezoidal area)');ax.legend();save(partname+'_PR')
 # Archived threshold evidence is retained; plotting uses a fixed descriptive grid only.
 f=d.iloc[slice(*B14)];p=probs(original(),f);y=f.f_nv.to_numpy();s=p[:,1:4].sum(1);h=np.isin(y,[1,2,3]);rows=[]
 for t in np.linspace(0,1,151):
  z=s>=t;rows.append({'threshold':t,'hardware_recall':z[h].mean(),'combined_nonhardware_FPR':z[~h].mean(),'precision':h[z].mean() if z.any() else None})
 csv('evidence/rubric3/threshold_curve_block14.csv',rows);fig,ax=plt.subplots(figsize=(7,4))
 for k in ['hardware_recall','combined_nonhardware_FPR','precision']:ax.plot([r['threshold'] for r in rows],[r[k] for r in rows],label=k)
 ax.axvline(.5913558658757772,linestyle='--',color='black',label='Archived tau; not retuned');ax.set(xlabel='p1+p2+p3 threshold',ylabel='Rate',title='Original probabilities, VALIDATION block14');ax.legend();save('archived_threshold_curve')
 shift=load('evidence/rubric4/shift.json')['results'];fig,axes=plt.subplots(1,2,figsize=(10,3))
 for name in ['VALIDATION','TEST']:
  r=[v for v in shift if v['partition']==name];axes[0].plot([v['sensor'] for v in r],[v['PSI'] for v in r],marker='o',label=name);axes[1].plot([v['sensor'] for v in r],[v['KS_statistic'] for v in r],marker='o',label=name)
 axes[0].set_title('TRAIN-decile PSI');axes[1].set_title('KS effect size (no iid p-value claim)');axes[0].legend();save('source_cohort_shift')
 stress=load('evidence/rubric4/stress.json');noise=[r for r in stress['results'] if r['experiment']=='Gaussian_noise_TRAIN_IQR'];fig,ax=plt.subplots(figsize=(6,4))
 for seed in [42,43,44]:
  r=[v for v in noise if v['seed']==seed];ax.plot([v['amount']*100 for v in r],[v['macro_f1_fixed_five'] for v in r],marker='o',label='seed'+str(seed))
 ax.axhline(stress['baseline']['macro_f1_fixed_five'],color='black',linestyle='--',label='Unperturbed');ax.set(xlabel='Gaussian noise SD (% TRAIN IQR)',ylabel='Macro F1',title='Simulated perturbations, VALIDATION block13');ax.legend();save('simulated_noise')
 fig,ax=plt.subplots(figsize=(10,4));r=[v for v in stress['results'] if v['experiment']=='entire_channel_dropout'];continuous=load('evidence/rubric4/contiguous_dropout.json')['results'];positions=np.arange(4);ax.bar(positions-.18,[v['coverage'] for v in r],width=.36,label='Sparse sample; gaps reset eligibility');ax.bar(positions+.18,[v['coverage'] for v in continuous],width=.36,label='Full contiguous block13; only first2 eligible');ax.set_xticks(positions,CHANNELS);ax.set(ylabel='Eligible prediction coverage',title='Offline dropout: sampled gaps are not uninterrupted outage tolerance',ylim=(0,1));ax.legend();save('dropout_coverage')
 subgroup=load('evidence/rubric4/subgroups.json')['metrics'];fig,ax=plt.subplots(figsize=(8,4))
 for name in PARTS:
  r=[v for v in subgroup if v['partition']==name and v['variable']=='signal_block' and v['group']>0];ax.plot([v['group'] for v in r],[v['macro_f1_present_classes'] for v in r],marker='o',label=name)
 ax.set(xlabel='Signal-defined block (not a day/session)',ylabel='Supported-class macro F1',title='Class support differs; inspect subgroup JSON');ax.legend();save('block_performance')
 folds=OUT/'evidence/rubric2/grouped_validation.json'
 if folds.exists():
  rows=load('evidence/rubric2/grouped_validation.json')['folds'];fig,ax=plt.subplots(figsize=(7,4))
  for family in ['LR','RF','LightGBM']:
   r=[v for v in rows if v['family']==family];ax.plot([v['fold'] for v in r],[v['metrics']['macro_f1_present_classes'] for v in r],marker='o',label=family)
  ax.set(xlabel='Nonshuffled grouped fold',ylabel='Supported-class macro F1',title='TRAIN operating blocks: fold0 cannot learn class1');ax.legend();save('grouped_validation')
 print('FIGURES_COMPLETE',len(list(folder.glob('*.png'))),flush=True)
