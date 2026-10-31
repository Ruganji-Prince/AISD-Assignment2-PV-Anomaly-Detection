"""Actual approved preprocessing and training-only assignment diagnostics."""
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler,MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection import StratifiedShuffleSplit
from src.pipeline_builder import build_preprocessor
from src.transformers import RetainedQuality
from src.pipeline_builder import CONFIGS,schema,POLICIES
from src.transformers import eligible
from .common import *

CANDIDATES=list(POLICIES)
def fit_training_preprocessor(X,family,config):
 channels=list(CONFIGS[config]);schema(X,channels,training=True)
 result=build_preprocessor(family,channels)
 assert list(result.named_steps)==['quality','columns']
 result.fit(X)
 return result

class PreprocessingStudy:
 def __init__(self):self.stats={};self.preprocessors={};self.matrices={};self.figures=[]
 def load_data(self):
  path=ROOT/'data/raw/pv_fault_dataset.csv';assert sha(path)=='717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a'
  self.raw=pd.read_csv(path,dtype={'f_nv':'uint8'},float_precision='round_trip');assert self.raw.shape==(1373798,7) and list(self.raw)==SENSORS+['f_nv']
  self.raw.index.name='source_position'
  missing=self.raw.isna().sum();paired=int(((self.raw.irr==0)&(self.raw.pvt==0)).sum())
  assert int(missing.sum())==0 and paired==62
  self.stats['raw_audit']={'N':len(self.raw),'P':7,'columns':list(self.raw),'missing_counts':{c:int(v) for c,v in missing.items()},'overall_missing_pct':0.,'paired_zero_observations':paired,'negative_irradiance_observations':int((self.raw.irr<0).sum()),'negative_Celsius_observations':int((self.raw.pvt<0).sum()),'raw_sha256':sha(path),'target':'Five nominal f_nv labels; no ordinal/continuous interpretation.'}
  print(self.raw.dtypes.to_string());print('Raw shape:',self.raw.shape,'; conventional missing cells:',int(missing.sum()),'; paired zeros retained:',paired)
 def split_data(self):
  self.partitions={n:self.raw.iloc[a:b].copy() for n,(a,b) in [('TRAIN',TRAIN),('VALIDATION',VALIDATION),('TEST',TEST)]}
  self.stats['splits']={n:{'interval':[int(x.index[0]),int(x.index[-1])+1],'N':len(x),'index_digest':digest(x.index)} for n,x in self.partitions.items()}
  self.stats['excluded_separator_intervals']=[[1006129,1056990],[1173967,1227337]]
  assert sum(len(x) for x in self.partitions.values())+104231==len(self.raw)
  self.stats['fit_ledger']=[]
  print(pd.DataFrame(self.stats['splits']).T.to_string())
 def model_ready(self):
  public=load('phase2_implementation/compliance/Preprocessing_Reference.json')['model_ready'];train=self.partitions['TRAIN']
  blocks=load('phase1_strategy/Phase1_Split_Manifest.json')['operating_blocks'];boundaries=tuple(sorted({v for b in blocks for v in [b['start'],b['end_exclusive']]}))
  self.stats['model_ready']={};self.stats['preprocessing_only']=True
  for key in CANDIDATES:
   family,config=POLICIES[key];channels=list(CONFIGS[config]);X=train[channels];pre=fit_training_preprocessor(X,family,config);self.preprocessors[key]=pre
   median=pre.named_steps['columns'].named_transformers_['numeric'].named_steps['median'].statistics_
   assert np.array_equal(median,np.asarray(public[key]['medians']))
   names=pre.get_feature_names_out().tolist();assert names==public[key]['feature_names']
   assert not any(bad in name for name in names for bad in ['source_position','block_id','timestamp','f_nv'])
   self.stats['fit_ledger'].append({'component':key+' median/scaler/feature schema','population':'TRAIN','N':len(X),'index_digest':digest(X.index),'raw_channels':channels})
   self.matrices[key]={};summary={}
   for partition,frame in self.partitions.items():
    transformed=pre.transform(frame[channels]);clean=pre.named_steps['quality'].transform(frame[channels]);mask=eligible(clean,boundaries)
    assert transformed.shape==(len(frame),len(names)) and np.isfinite(transformed).all()
    self.matrices[key][partition]=transformed;summary[partition]={'shape':list(transformed.shape),'eligible_rows':int(mask.sum()),'target_rows':len(frame.f_nv),'fitted_again':False}
   self.stats['model_ready'][key]={'raw_channels':channels,'feature_names':names,'medians':median.tolist(),'partitions':summary}
   print(key,summary)
  lr=self.preprocessors['six_standard'];numeric=lr.named_steps['columns'].named_transformers_['numeric'];self.training_clean=lr.named_steps['quality'].transform(train[SENSORS]);self.training_numeric=numeric.named_steps['median'].transform(self.training_clean);self.standard=numeric.named_steps['scale'];assert int(self.standard.n_samples_seen_)==TRAIN[1]
  self.standardized=self.standard.transform(self.training_numeric)
  self.stats['reference_cleaning']={'population':'TRAIN','rows_before':len(train),'rows_after':len(self.training_clean),'removed_rows':0,'winsorized_cells':0,'changed_cells':{c:int((train[c]!=self.training_clean[c]).sum()) for c in SENSORS},'policy':'Existing RetainedQuality only; paired zeros and negative Celsius retained; no automatic statistical capping/deletion.'}
 def associations(self):
  train=self.partitions['TRAIN'];self.correlation=train[SENSORS].corr(method='pearson');assert list(self.correlation)==SENSORS
  frozen=pd.read_csv(ROOT/'phase1_strategy/Training_Correlation.csv',index_col=0);assert np.allclose(self.correlation.to_numpy(),frozen.to_numpy(),rtol=0,atol=1e-12)
  self.high_pairs=[(a,b,float(self.correlation.loc[a,b])) for i,a in enumerate(SENSORS) for b in SENSORS[i+1:] if abs(self.correlation.loc[a,b])>=.85]
  assert len(self.high_pairs)==5
  rng=np.random.default_rng(SEED);self.scatter_positions=np.sort(rng.choice(len(train),20000,replace=False))
  splitter=StratifiedShuffleSplit(n_splits=1,train_size=50000,random_state=SEED);positions,_=next(splitter.split(self.training_numeric,train.f_nv));positions=np.sort(positions)
  assert np.all((positions>=TRAIN[0])&(positions<TRAIN[1]))
  self.mi=mutual_info_classif(self.standardized[positions],train.f_nv.to_numpy()[positions],discrete_features=False,n_neighbors=3,random_state=SEED,n_jobs=2)
  self.stats['correlation']={'population':'TRAIN','N':len(train),'columns':SENSORS,'target_excluded':True,'matrix':self.correlation.to_numpy().tolist(),'high_pairs':[list(x) for x in self.high_pairs],'matches_Phase1':True}
  self.stats['scatter_sample']={'population':'TRAIN','N':20000,'seed':SEED,'sampling':'Uniform without replacement from all training source positions; sorted for display.','index_digest':digest(train.index[self.scatter_positions])}
  self.stats['mutual_information']={'population':'TRAIN','N':50000,'seed':SEED,'sampling':'Seeded proportional stratified sample without replacement; natural training prevalence approximately preserved. Not model resampling.','class_counts':{str(k):int(v) for k,v in train.f_nv.iloc[positions].value_counts().sort_index().items()},'index_digest':digest(train.index[positions]),'method':'mutual_info_classif; continuous X, nominal discrete target; k=3; standardized with TRAIN-fitted scaler. Dependent observations/ties limit interpretation; diagnostic associations, not significance or causal effects.','scores_nats':dict(zip(SENSORS,self.mi.tolist()))}
  print('Training |r| >= .85 pairs:',self.high_pairs);print('Training-sample mutual information (nats):',self.stats['mutual_information']['scores_nats'])
 def scaling_and_pca(self):
  self.robust=RobustScaler().fit(self.training_numeric);self.minmax=MinMaxScaler().fit(self.training_numeric)
  self.pca=PCA(n_components=6,svd_solver='full').fit(self.standardized);assert self.pca.n_samples_==TRAIN[1]
  for component in ['RobustScaler alternative','MinMaxScaler alternative','Standard-scaled exploratory PCA']:
   self.stats['fit_ledger'].append({'component':component,'population':'TRAIN','N':TRAIN[1],'index_digest':digest(self.partitions['TRAIN'].index),'diagnostic_only':True})
  evr=self.pca.explained_variance_ratio_;cum=np.cumsum(evr)
  self.stats['PCA']={'population':'TRAIN','N':int(self.pca.n_samples_),'input_columns':SENSORS,'scaled_with':'Existing StandardScaler fitted on TRAIN only','explained_variance_ratio':evr.tolist(),'cumulative_explained_variance':cum.tolist(),'components_for_90pct':int(np.searchsorted(cum,.90)+1),'components_for_95pct':int(np.searchsorted(cum,.95)+1),'deployment_role':'Exploratory diagnostic only; no physical sensor reduction without selecting physical channels.'}
  self.stats['scaling']={'population':'TRAIN','N':TRAIN[1],'standardized_policy':'StandardScaler on numerical channels; availability indicators unchanged.','native_policy':'Native numerical scale.','diagnostic_alternatives':['RobustScaler','MinMaxScaler'],'log_transform':'Not applied; optional nonnegative log1p was not selected in the frozen primary pipeline.','standard_mean':self.standard.mean_.tolist(),'standard_scale':self.standard.scale_.tolist(),'robust_center':self.robust.center_.tolist(),'robust_scale':self.robust.scale_.tolist(),'minmax_data_min':self.minmax.data_min_.tolist(),'minmax_data_max':self.minmax.data_max_.tolist()}
  print('Exploratory PCA:',self.stats['PCA'])
 def save_evidence(self):
  self.stats['classifier_training_calls']=0;self.stats['classifier_predictions_generated']=False;self.stats['preprocessing_decisions_changed']=False
  write(OUT/'Preprocessing_Evidence.json',self.stats);write(OUT/'Diagnostic_Inventory.json',self.figures)
  print('Saved compact preprocessing evidence; 0 classifier fits/predictions.')
