"""Training-only Pipeline/ColumnTransformer models and separate binary rule reference."""
import json
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer,MissingIndicator
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from .features import Quality,PhysicalFeatures,eligible
from .contracts import ROOT,SENSORS,SEED,TRAIN,BLOCK13,train_only,index_digest,validate_predictors

class F6Model:
 def __init__(self,family,policy,params,class_weights):
  if family not in ['LR','RF','LightGBM'] or policy not in ['raw','engineered']:raise ValueError('Unsupported family/policy')
  if family!='LightGBM' and policy!='raw':raise ValueError('Stage 1 engineering comparison is bounded to LightGBM')
  self.family=family;self.policy=policy;self.params=params;self.class_weights=class_weights
  numeric=[('median',SimpleImputer(strategy='median',keep_empty_features=True))]
  if policy=='engineered':numeric.append(('physical',PhysicalFeatures()))
  if family=='LR':numeric.append(('scale',StandardScaler()))
  columns=ColumnTransformer([('numeric',Pipeline(numeric),SENSORS),
   ('missing',MissingIndicator(features='all',error_on_new=False),SENSORS)],remainder='drop',sparse_threshold=0)
  if family=='LR':est=LogisticRegression(**params,class_weight=class_weights,max_iter=2000,solver='lbfgs',random_state=SEED)
  elif family=='RF':est=RandomForestClassifier(**params,n_estimators=100,min_samples_leaf=20,class_weight=class_weights,n_jobs=2,random_state=SEED)
  else:est=LGBMClassifier(**params,objective='multiclass',num_class=5,class_weight=class_weights,
   n_estimators=150,learning_rate=.05,min_child_samples=50,max_bin=127,reg_lambda=1.,
   deterministic=True,force_col_wise=True,n_jobs=2,random_state=SEED,verbosity=-1)
  self.pipeline=Pipeline([('quality',Quality()),('columns',columns),('model',est)])
  split=json.loads((ROOT/'phase1_strategy/Phase1_Split_Manifest.json').read_text())
  self.boundaries=tuple(sorted({v for b in split['operating_blocks'] for v in [b['start'],b['end_exclusive']]}))
 def fit(self,X,y):
  train_only(X);self.pipeline.fit(X,y);self.fit_index_digest_=index_digest(X.index)
  self.fit_rows_=len(X);self.classes_=self.pipeline.named_steps['model'].classes_;return self
 def transformed(self,X):validate_predictors(X);return self.pipeline[:-1].transform(X)
 def predict_proba(self,X):
  validate_predictors(X)
  if len(X) and not (((X.index>=TRAIN[0])&(X.index<TRAIN[1]))|((X.index>=BLOCK13[0])&(X.index<BLOCK13[1]))).all():
   raise ValueError('Stage 1 predictions restricted to training and block 13; block 14/test disabled.')
  clean=self.pipeline.named_steps['quality'].transform(X)
  p=self.pipeline[1:].predict_proba(clean);p[~eligible(clean,self.boundaries)]=np.nan;return p
 def names(self):return self.pipeline.named_steps['columns'].get_feature_names_out().tolist()

class EngineeringReference:
 """Binary F6 paired-string discrepancy reference, not a five-class classifier."""
 def fit(self,X,y):
  train_only(X);self.quality=Quality().fit(X);clean=self.quality.transform(X)
  self.medians_=clean.median();d=self._difference(clean.fillna(self.medians_))[np.asarray(y)==0]
  self.center_=np.median(d,axis=0);self.iqr_=np.quantile(d,.75,axis=0)-np.quantile(d,.25,axis=0)
  self.fit_index_digest_=index_digest(X.index);return self
 def _difference(self,X):
  return np.column_stack([np.abs(X.idc1-X.idc2)/(X.idc1+X.idc2+.1),np.abs(X.vdc1-X.vdc2)/(X.vdc1+X.vdc2+1.)])
 def score(self,X):
  z=self.quality.transform(X);return np.maximum(0,((self._difference(z.fillna(self.medians_))-self.center_)/(self.iqr_+1e-6)).max(axis=1))
