"""Declared validation-only rankings; no final engineering acceptance."""
import numpy as np


def pass_flags(row):
 return {'macro_f1_ge_080':row['macro_f1']>=.80,'each_hardware_recall_ge_090':min(row['class1_recall'],row['class2_recall'],row['class3_recall'])>=.90,
  'delta_le_005':row['delta_s']<=.05,'channels_le_4':row['physical_channels']<=4,
  'p95_le_10ms':row['p95_ms']<=10.,'artifact_le_10MiB':row['artifact_MiB']<=10.}


def select(rows):
 def perf(z):return (-z['macro_f1'],-z['hardware_macro_recall'],z['artifact_MiB'],z['key'])
 f6=min([r for r in rows if r['configuration']=='F6' and r['converged']],key=perf)
 sparse=[r for r in rows if r['physical_channels']<=4 and r['converged']]
 best_sparse=min(sparse,key=perf)
 passes=[r for r in sparse if all(r['criteria'][k] for k in ['macro_f1_ge_080','each_hardware_recall_ge_090','delta_le_005','channels_le_4'])]
 minimum=min(passes,key=lambda z:(z['physical_channels'],)+perf(z)) if passes else None
 # A compromise must first satisfy current predictive/degradation and measured resource conditions.
 compromises=[r for r in rows if r['converged'] and all(r['criteria'][k] for k in ['macro_f1_ge_080','each_hardware_recall_ge_090','delta_le_005','p95_le_10ms','artifact_le_10MiB'])]
 compromise=min(compromises,key=lambda z:(z['physical_channels'],z['p95_ms'],z['artifact_MiB'])+perf(z)) if compromises else None
 shortlist=list(dict.fromkeys([r['key'] for r in [f6,best_sparse,minimum,compromise] if r is not None]))
 return {'best_F6':f6['key'],'best_at_most_4_channels':best_sparse['key'],
  'minimum_channel_currently_passing':None if minimum is None else minimum['key'],
  'resource_performance_candidate':None if compromise is None else compromise['key'],'shortlist_before_dropout':shortlist,
  'ranking_logic':{'best_F6_and_best_sparse':'Highest macro-F1, then hardware macro recall, smaller artifact, identifier.',
   'minimum_channel_passing':'Fewest channels among candidates passing four current criteria; then performance ranking.',
   'resource_performance':'Pass predictive/degradation and measured resource criteria; then fewest channels, lower p95, smaller size, performance.',
   'dropout':'Evaluated after this shortlist is frozen; does not change these Stage 2 selections.'},
  'final_engineering_acceptance':False,'remaining_stage3_items':['block-14 equipment alert threshold and FPR','later revised test evaluation with prior-exposure disclosure'],
  'missing_candidate_policy':'Null means no candidate satisfies that declared rule; no fallback is silently relabeled as passing.'}
