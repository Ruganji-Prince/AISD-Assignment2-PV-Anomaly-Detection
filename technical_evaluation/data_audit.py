import itertools,hashlib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_classif
from sklearn.neighbors import NearestNeighbors
from .common import *

def vector_hash(frame):
 a=np.asarray(frame,dtype='<f8').copy();a[a==0]=0
 return np.array([hashlib.blake2b(row.tobytes(),digest_size=16).hexdigest() for row in a],dtype='U32')

def main():
 d=raw();train=part(d,'TRAIN');rows=[]
 for c in d:
  values=d[c].to_numpy();missing=int(pd.isna(values).sum());rows.append({'column':c,'type':'nominal integer target' if c=='f_nv' else 'continuous float64','missing_N':missing,'missing_pct':missing/len(d)*100,'infinite_N':int(np.isinf(values).sum()),'zero_N':int((values==0).sum()),'negative_N':int((values<0).sum())})
 csv('evidence/rubric1/missingness.csv',rows)
 write('evidence/rubric1/missingness.json',{'N':len(d),'P':7,'overall_missing_pct':float(d.isna().to_numpy().mean()*100),'complete_rows':int(d.notna().all(axis=1).sum()),'incomplete_rows':int(d.isna().any(axis=1).sum()),'paired_irr_pvt_zero_N':int(((d.irr==0)&(d.pvt==0)).sum()),'Little_MCAR':{'status':'NOT APPLICABLE','reason':'All exported missingness indicators are constant zero; no incomplete missing-data patterns or estimable missingness mechanism.'},'Cramer_V_missingness_target':{'status':'NOT APPLICABLE','reason':'Missingness-versus-target table has one constant missingness category; denominator min(r-1,c-1)=0.'},'MCAR_MAR_MNAR':'Not identifiable from zero exported NaNs. Suspicious paired zeros remain observations, not confirmed missingness.','columns':rows})
 stats_rows=[];rng=np.random.default_rng(SEED)
 for c in SENSORS:
  x=train[c].to_numpy();q1,q3=np.quantile(x,[.25,.75]);iqr=q3-q1;lo,hi=q1-1.5*iqr,q3+1.5*iqr;med=np.median(x);mad=np.median(abs(x-med));sd=x.std();sample=rng.choice(x,min(10000,len(x)),replace=False);normal=stats.normaltest(sample)
  stats_rows.append({'sensor':c,'N':len(x),'q1':q1,'q3':q3,'IQR':iqr,'IQR_lower':lo,'IQR_upper':hi,'IQR_flagged':int(((x<lo)|(x>hi)).sum()),'zscore_abs_gt3':int((abs((x-x.mean())/sd)>3).sum()) if sd else 0,'MAD':mad,'modified_z_abs_gt3_5':int((abs(.67448975*(x-med)/mad)>3.5).sum()) if mad else None,'skewness':stats.skew(x),'normaltest_stat_sample10000':normal.statistic,'normaltest_p_diagnostic_only':normal.pvalue,'normality_test_limitation':'Dependent readings; diagnostic distribution shape, not independent evidence of fault validity.'})
 csv('evidence/rubric1/training_outliers.csv',stats_rows)
 pearson=train[SENSORS].corr();spearman=train[SENSORS].corr(method='spearman');pearson.to_csv(OUT/'evidence/rubric1/Pearson.csv');spearman.to_csv(OUT/'evidence/rubric1/Spearman.csv')
 sample_idx=np.sort(rng.choice(len(train),50000,replace=False));a=train[SENSORS].to_numpy();scaled=StandardScaler().fit_transform(a);vif={}
 for i,c in enumerate(SENSORS):
  z=np.column_stack([np.ones(len(a)),np.delete(scaled,i,axis=1)]);coef=np.linalg.lstsq(z,scaled[:,i],rcond=None)[0];r2=1-np.square(scaled[:,i]-z@coef).sum()/np.square(scaled[:,i]-scaled[:,i].mean()).sum();vif[c]=float(1/(1-r2))
 mi=mutual_info_classif(scaled[sample_idx],train.f_nv.iloc[sample_idx],random_state=SEED,n_jobs=2);pca=PCA(n_components=6,svd_solver='full').fit(scaled)
 write('evidence/rubric1/feature_screening.json',{'population':'TRAIN only','N':len(train),'Pearson_abs_ge_085':[(a,b,float(pearson.loc[a,b])) for i,a in enumerate(SENSORS) for b in SENSORS[i+1:] if abs(pearson.loc[a,b])>=.85],'Spearman_abs_ge_085':[(a,b,float(spearman.loc[a,b])) for i,a in enumerate(SENSORS) for b in SENSORS[i+1:] if abs(spearman.loc[a,b])>=.85],'VIF':vif,'VIF_threshold':10,'MI_nats':dict(zip(SENSORS,mi)),'MI_population':'Seed42 natural-prevalence TRAIN sample 50000; diagnostic not significance or causal evidence.','PCA_explained_variance_ratio':pca.explained_variance_ratio_,'PCA_cumulative':pca.explained_variance_ratio_.cumsum(),'decision':'No deployed feature or transformation change. Correlated channel groups retained pending sensor-ablation evidence; PCA requires physical parent inputs and is not sensor reduction.','inference_features':CHANNELS,'target_or_metadata_features':[]})
 # Exact source-position and operating-block integrity, including ungrouped background rows.
 membership=np.full(len(d),-1);parts={}
 for j,(name,(lo,hi)) in enumerate(PARTS.items()):membership[lo:hi]=j;parts[name]={'bounds':[lo,hi],'N':hi-lo,'index_digest':digest(np.arange(lo,hi)),'operating_blocks':sorted(set(groups(np.arange(lo,hi)))-{0})}
 assert int((membership==-1).sum())==104231
 for x,y in itertools.combinations(parts,2):assert not set(parts[x]['operating_blocks'])&set(parts[y]['operating_blocks'])
 leakage={'partitions':parts,'separator_intervals':[[1006129,1056990],[1173967,1227337]],'excluded_N':int((membership==-1).sum()),'source_index_disjoint':True,'operating_blocks_disjoint':True,'background_rows':'Block 0 means positions outside signal-defined operating intervals; it is not a shared acquisition-session identifier.','timestamps':'Absent; blocks and resampling tiles are not verified days/sessions/hours.','feature_vectors':{}}
 for label,features in [('six_physical',SENSORS),('four_deployed',CHANNELS)]:
  h=vector_hash(d[features]);frame=pd.DataFrame({'hash':h,'label':d.f_nv,'partition':membership});gb=frame.groupby('hash',sort=False).agg(N=('label','size'),minimum_label=('label','min'),maximum_label=('label','max'))
  overlap=[]
  for x,y in itertools.combinations(PARTS,2):
   xi=list(PARTS).index(x);yi=list(PARTS).index(y);xp=np.flatnonzero(membership==xi);yp=np.flatnonzero(membership==yi);xh,xx=np.unique(h[xp],return_index=True);yh,yy=np.unique(h[yp],return_index=True);inter,ix,iy=np.intersect1d(xh,yh,return_indices=True);ax=xp[xx[ix]];ay=yp[yy[iy]];assert np.array_equal(d.iloc[ax][features].to_numpy(),d.iloc[ay][features].to_numpy());verified=len(inter)
   overlap.append({'first':x,'second':y,'shared_distinct_feature_vectors':verified})
  conflicts=gb[gb.minimum_label!=gb.maximum_label];examples=[]
  for key in conflicts.index[:10]:
   pos=np.flatnonzero(h==key);assert np.all(d.iloc[pos][features].to_numpy()==d.iloc[pos[0]][features].to_numpy());examples.append({'count':len(pos),'labels':sorted(d.f_nv.iloc[pos].unique().tolist()),'partitions':sorted(set(membership[pos].tolist()))})
  leakage['feature_vectors'][label]={'hash':'BLAKE2b-128 over canonical float64 values; cross-split matches independently checked by exact vector equality','features':features,'duplicate_distinct_vectors':int((gb.N>1).sum()),'rows_in_duplicates':int(gb.loc[gb.N>1,'N'].sum()),'conflicting_label_vectors':len(conflicts),'cross_partition_overlap':overlap,'conflict_examples':examples}
  CACHE.mkdir(parents=True,exist_ok=True);np.save(CACHE/(label+'_hash.npy'),h)
  print('EXACT_VECTOR_AUDIT',label,overlap,'conflicts',len(conflicts),flush=True)
 # Bounded near-neighbor screen uses no target for scaling/reference fitting.
 scaler=StandardScaler().fit(train[CHANNELS]);idx=np.sort(rng.choice(len(train),100000,replace=False));ref=scaler.transform(train[CHANNELS].iloc[idx]);nn=NearestNeighbors(n_neighbors=1,n_jobs=2).fit(ref);near=[]
 for name in ['VALIDATION','TEST']:
  q=part(d,name);selected=np.sort(rng.choice(len(q),min(5000,len(q)),replace=False));dist,_=nn.kneighbors(scaler.transform(q[CHANNELS].iloc[selected]));near.append({'partition':name,'query_N':len(selected),'TRAIN_reference_N':len(idx),'distance':'Euclidean in TRAIN-standardized physical E4 coordinates','min':dist.min(),'median':np.median(dist),'q01':np.quantile(dist,.01),'within_1e_3':int((dist<=1e-3).sum()),'limitation':'Bounded diagnostic, not an exhaustive near-duplicate proof or automatic leakage declaration.'})
 leakage['near_duplicate_diagnostics']=near;write('evidence/rubric2/leakage.json',leakage)
 write('evidence/rubric2/TRAIN_block_support.json',[{'block':b['block'],'N':b['N'],'classes':d.iloc[b['start']:b['end_exclusive']].f_nv.value_counts().sort_index().to_dict()} for b in blocks()[:12]])
 print('DATA_AND_LEAKAGE_AUDIT_COMPLETE',flush=True)
