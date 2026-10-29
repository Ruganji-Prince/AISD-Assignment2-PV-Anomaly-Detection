"""Eight deterministic assignment plots; all fitted diagnostics are TRAIN-only."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap,BoundaryNorm
from matplotlib.cbook import boxplot_stats
from PIL import Image
from .common import *
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})

def save(study,fig,number,name,title,caption,population='TRAINING ONLY'):
 FIGURES.mkdir(exist_ok=True,parents=True);fig.tight_layout();path=FIGURES/name;fig.savefig(path,dpi=300,bbox_inches='tight');plt.close(fig)
 with Image.open(path) as im:size=list(im.size)
 record={'number':number,'file':path.relative_to(ROOT).as_posix(),'title':title,'caption':caption,'population':population,'dpi':300,'dimensions_px':size,'bytes':path.stat().st_size,'sha256':sha(path)}
 study.figures.append(record);print('Diagnostic',number,path.relative_to(ROOT).as_posix());return record

def missingness(study):
 train=study.partitions['TRAIN'];positions=np.sort(np.random.default_rng(SEED).choice(len(train),5000,replace=False));mask=train.iloc[positions].isna().to_numpy().astype(int)
 fig,ax=plt.subplots(figsize=(7.4,4));cmap=ListedColormap(['#e5eff7','#b63535']);im=ax.imshow(mask,aspect='auto',interpolation='nearest',cmap=cmap,norm=BoundaryNorm([-.5,.5,1.5],2));ax.set_xticks(range(7),SENSORS+['f_nv']);ax.set_ylabel('Displayed sampled observation (not time)');ax.set_xlabel('Released variables');ax.set_title('TRAINING ONLY — missingness display; seeded N = 5,000')
 bar=fig.colorbar(im,ax=ax,ticks=[0,1]);bar.ax.set_yticklabels(['Observed','Missing (none observed)'])
 return save(study,fig,1,'fig1_1_missingness_heatmap.png','Missingness pattern','Seed-42 uniform TRAIN display. Full released-data audit: 0 conventional missing cells across all seven variables. The 62 paired zeros remain observations, not confirmed missing values.')

def target_distribution(study):
 counts=study.partitions['TRAIN'].f_nv.value_counts().sort_index();fig,ax=plt.subplots(figsize=(8.3,4));bars=ax.bar(range(5),counts,color=['#245b8a','#bd6428','#348261','#8466a0','#c4a245']);ax.set_xticks(range(5),[str(k)+'\n'+n for k,n in enumerate(LABELS)],fontsize=8);ax.set_ylabel('Training observations (linear count)');ax.set_ylim(0,counts.max()*1.22);ax.ticklabel_format(axis='y',style='plain');ax.set_title('TRAINING ONLY — five nominal operating states; N = 1,006,129')
 for bar,n in zip(bars,counts):ax.annotate(f'{n:,}\n{100*n/counts.sum():.3f}%',(bar.get_x()+bar.get_width()/2,n),xytext=(0,5),textcoords='offset points',ha='center',fontsize=8)
 return save(study,fig,2,'fig1_2_target_distribution.png','Target class distribution','All TRAIN labels, without rebalancing. Counts and percentages expose rare hardware states; accuracy alone is inadequate. Class 4 is natural building shade, not hardware failure.')

def outliers(study):
 raw=study.partitions['TRAIN'];clean=study.training_clean;fig,axes=plt.subplots(2,3,figsize=(10.7,6.4))
 for ax,c in zip(axes.ravel(),SENSORS):
  boxes=boxplot_stats([raw[c].to_numpy(),clean[c].to_numpy()],labels=['Raw','Reference-cleaned'],whis=1.5)
  result=ax.bxp(boxes,showfliers=True,patch_artist=True,flierprops={'marker':'.','markersize':1.3,'alpha':.20,'markeredgecolor':'#333333'})
  for box,color in zip(result['boxes'],['#a9c7dd','#b8d2bb']):box.set_facecolor(color)
  ax.set_ylabel(c+' ('+UNITS[c]+')');ax.tick_params(axis='x',labelsize=8);ax.grid(axis='y',alpha=.15)
 fig.suptitle('TRAINING ONLY — raw versus approved reference cleaning; no statistical capping/deletion',fontsize=11)
 return save(study,fig,3,'fig2_1_outlier_boxplots.png','Raw vs reference-cleaned boxplots','Full TRAIN IQR box statistics and fliers are shown. Reference cleaning is the existing RetainedQuality policy; unusual values remain. Nearly identical panels reflect intentional retention, not failed cleaning. Units are channel-specific.')

def correlation(study):
 a=study.correlation.to_numpy();mask=np.tril(np.ones((6,6),dtype=bool));masked=np.ma.masked_where(mask,a);fig,ax=plt.subplots(figsize=(6.6,5.5));im=ax.imshow(masked,cmap='coolwarm',vmin=-1,vmax=1);ax.set_xticks(range(6),SENSORS);ax.set_yticks(range(6),SENSORS);ax.set_xlabel('Predictor');ax.set_ylabel('Predictor');ax.set_title('TRAINING ONLY — upper-triangle Pearson correlation')
 for i in range(6):
  for j in range(i+1,6):
   high=abs(a[i,j])>=.85;ax.text(j,i,f'{a[i,j]:.3f}'+('*' if high else ''),ha='center',va='center',fontsize=9,fontweight='bold' if high else 'normal',color='white' if a[i,j]>.7 else 'black')
 fig.colorbar(im,ax=ax,label='Pearson r (predictors only)')
 return save(study,fig,4,'fig3_1_correlation_matrix.png','Training predictor correlation','All six raw TRAIN predictors; f_nv is excluded. Asterisks mark |r| >= 0.85 (five pairs), matching Phase 1. Screening warns about redundancy; the frozen reference retains physical channels pending the predeclared ablation, rather than automatically dropping them.')

def collinear_pairs(study):
 raw=study.partitions['TRAIN'];sample=raw.iloc[study.scatter_positions];fig,axes=plt.subplots(2,3,figsize=(11.3,6.4))
 for ax,(a,b,r) in zip(axes.ravel(),study.high_pairs):
  ax.scatter(sample[a],sample[b],s=2,alpha=.13,color='#245b8a',rasterized=True)
  slope=r*raw[b].std()/raw[a].std();intercept=raw[b].mean()-slope*raw[a].mean();x=np.array([raw[a].min(),raw[a].max()]);ax.plot(x,intercept+slope*x,color='#bd6428',lw=1.3,label='Full-TRAIN OLS line')
  ax.set_xlabel(a+' ('+UNITS[a]+')');ax.set_ylabel(b+' ('+UNITS[b]+')');ax.set_title(f'{a} / {b}: full-TRAIN r = {r:.3f}');ax.legend(fontsize=7)
 for ax in axes.ravel()[len(study.high_pairs):]:ax.axis('off')
 fig.suptitle('TRAINING ONLY — seeded uniform display N = 20,000 of 1,006,129',fontsize=11)
 return save(study,fig,5,'fig3_2_collinear_scatterplots.png','Collinear predictor pairs','All five Phase 1 high-correlation pairs. Points are a uniform seed-42 TRAIN sample; correlations and descriptive OLS lines use full TRAIN. Association is not causation; dependence precludes naive significance claims.')

def feature_target(study):
 order=np.argsort(study.mi);fig,ax=plt.subplots(figsize=(7.3,4));ax.barh(np.asarray(SENSORS)[order],study.mi[order],color='#348261');ax.set_xlabel('Estimated mutual information with nominal f_nv (nats)');ax.set_ylabel('Continuous predictor');ax.set_title('TRAINING ONLY — feature–target association; proportional sample N = 50,000')
 return save(study,fig,6,'fig3_3_target_importance.png','Feature-target mutual information','Seed-42 proportional stratified TRAIN sample, k=3 continuous-feature MI estimator; train-fitted standardization. Target codes remain nominal. This descriptive diagnostic does not alter frozen model/feature choices; imbalance, repeated readings and ties limit interpretation.')

def transformation_grid(study):
 i=SENSORS.index('irr');native=study.training_numeric[:,i]
 panels=[('Raw exported irradiance',study.partitions['TRAIN'].irr.to_numpy(),'W/m²'),('StandardScaler — selected LR',study.standardized[:,i],'standard deviations'),('RobustScaler — diagnostic alternative',study.robust.transform(study.training_numeric)[:,i],'median/IQR units'),('MinMaxScaler — diagnostic alternative',study.minmax.transform(study.training_numeric)[:,i],'training-range units')]
 fig,axes=plt.subplots(2,2,figsize=(9,6))
 for ax,(title,values,unit) in zip(axes.ravel(),panels):
  ax.hist(values,bins=60,color='#245b8a',alpha=.85);ax.set_yscale('log');ax.set_title(title,fontsize=10);ax.set_xlabel('irr ('+unit+')');ax.set_ylabel('Observations (log count)')
 fig.suptitle('TRAINING ONLY — 2 × 2 irradiance representation/scaling grid',fontsize=11)
 return save(study,fig,7,'fig4_1_transformation_grid.png','Transformation/scaling comparison','All learned scaler parameters use full TRAIN. Scaling changes units, not the underlying skewed shape. StandardScaler aligns LR regularization; RF/LightGBM retain native scale. Robust/MinMax are diagnostic alternatives only. Optional log1p is not introduced into frozen pipelines.')

def pca(study):
 ratios=study.pca.explained_variance_ratio_;cumulative=np.cumsum(ratios);x=np.arange(1,7);fig,ax=plt.subplots(figsize=(7.3,4));ax.bar(x,ratios,color='#a9c7dd',label='Explained variance ratio');ax.set_xlabel('Mathematical principal component');ax.set_ylabel('Individual variance fraction');ax.set_ylim(0,1.05);ax.set_xticks(x);other=ax.twinx();other.plot(x,cumulative,'o-',color='#bd6428',label='Cumulative variance');other.axhline(.90,color='#348261',ls='--',lw=1,label='90% threshold');other.axhline(.95,color='#8466a0',ls=':',lw=1,label='95% threshold');other.set_ylabel('Cumulative variance fraction');other.set_ylim(0,1.05);other.legend(fontsize=8,loc='center right');ax.legend(fontsize=8,loc='upper left');ax.set_title('TRAINING ONLY — StandardScaler + exploratory PCA; all six sensors')
 return save(study,fig,8,'fig5_1_pca_scree_plot.png','PCA scree and cumulative variance','StandardScaler and full-SVD PCA are fitted to full TRAIN only. PCA is an exploratory mathematical diagnostic, not physical sensor reduction, a feature-selection rule, or a change to the frozen models. All six inputs are needed to compute the components.')
