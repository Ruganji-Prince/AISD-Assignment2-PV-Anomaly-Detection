"""Existing preprocessing steps isolated from all downstream model dependencies."""
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer, MissingIndicator
from sklearn.preprocessing import StandardScaler
from src.transformers import RetainedQuality, PhysicalFeatures, SENSORS
CONFIGS={'F6':SENSORS,'E4':['vdc1','vdc2','idc1','idc2']}
POLICIES={'six_standard':('standard','F6'),'electrical_native':('native','E4'),'electrical_derived':('derived','E4')}
def schema(X,channels,training=False):
 if not isinstance(X,pd.DataFrame) or list(X.columns)!=list(channels):raise ValueError('Only retained raw predictors are permitted')
 if not X.index.is_unique or not X.index.is_monotonic_increasing:raise ValueError('Ordered unique source positions required')
 if training and (len(X)!=1006129 or not np.array_equal(X.index,np.arange(1006129))):raise ValueError('Fit restricted to TRAIN')
def build_preprocessor(policy,channels):
 if policy not in ['standard','native','derived'] or list(channels) not in list(CONFIGS.values()):raise ValueError('Unapproved preprocessing policy/channels')
 numeric=[('median',SimpleImputer(strategy='median',keep_empty_features=True))]
 if policy=='derived':numeric.append(('physical',PhysicalFeatures(channels)))
 if policy=='standard':numeric.append(('scale',StandardScaler()))
 columns=ColumnTransformer([('numeric',Pipeline(numeric),channels),('missing',MissingIndicator(features='all',error_on_new=False),channels)],remainder='drop',sparse_threshold=0)
 return Pipeline([('quality',RetainedQuality(channels)),('columns',columns)])
