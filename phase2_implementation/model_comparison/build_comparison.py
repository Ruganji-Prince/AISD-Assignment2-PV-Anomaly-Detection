"""Compare frozen evidence only: no scientific pipeline imports or model calls."""
from pathlib import Path
import argparse, csv, json, hashlib, subprocess, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
FIG=OUT/'figures';FIG.mkdir(exist_ok=True)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--evidence-root',type=Path,default=ROOT,help='Repository root containing the frozen evidence (defaults to this checkout).')
parser.add_argument('--git',default='git',help='Git executable used for read-only blob verification.')
args=parser.parse_args()
REC=args.evidence_root.resolve()
BASE=REC/'phase2_implementation/stage3/evidence'
COMMIT='34ab15ed18abb29defc0f30baa284f189fc05aef'
KEYS=['RF__E4','LightGBM__E4']; MODELS=['RF E4','LightGBM E4']
NAMES=['Normal','Short Circuit','Resistive Degradation','Open Circuit','Building Shade']
COLORS=['#246a9b','#d47a20']
inputs=['final_test_details.json','final_test_class_metrics.csv','final_candidate_comparison.csv','final_hardware_alert_metrics.csv']
evidence={}
git=args.git
for name in inputs:
    p=BASE/name;relative=p.relative_to(REC).as_posix();b=p.read_bytes()
    expected=subprocess.check_output([str(git),'rev-parse',f'{COMMIT}:{relative}'],cwd=ROOT,text=True).strip()
    assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==expected
    evidence[relative]={'sha256':hashlib.sha256(b).hexdigest(),'git_blob':expected}
protected=[p for p in (ROOT/'phase2_implementation/reports').glob('Phase2_Final_Report*') if p.suffix in ['.pdf','.md','.tex']]
before={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
details=json.loads((BASE/inputs[0]).read_text())
data={k:details['results'][k] for k in KEYS}
def records(name):
    with (BASE/name).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
classes={(r['candidate'],int(r['class'])):r for r in records(inputs[1]) if r['candidate'] in KEYS}
overall={r['candidate']:r for r in records(inputs[2]) if r['candidate'] in KEYS}
alerts={r['candidate']:r for r in records(inputs[3]) if r['candidate'] in KEYS}
rows=[];confusions=[]
for key,model in zip(KEYS,MODELS):
    d=data[key];cm=np.array(d['confusion_matrix'],dtype=int);supports=cm.sum(axis=1)
    assert cm.shape==(5,6) and supports.tolist()==[124512,2361,2270,2410,14908]
    assert cm.sum()==146461 and cm[:,5].sum()==0
    np.testing.assert_allclose(cm/supports[:,None],d['row_normalized_confusion_matrix'],rtol=0,atol=1e-15)
    for c in range(5):
        pc=d['per_class'][str(c)];raw=classes[key,c]
        for field in ['precision','recall','f1','AP','support']:assert math.isclose(float(raw[field]),pc[field],rel_tol=0,abs_tol=1e-15)
        tp=int(cm[c,c]);fp=int(cm[:,c].sum()-tp);fn=int(supports[c]-tp)
        assert math.isclose(tp/(tp+fp),pc['precision'],abs_tol=1e-15)
        assert math.isclose(tp/supports[c],pc['recall'],abs_tol=1e-15)
        assert math.isclose(2*tp/(2*tp+fp+fn),pc['f1'],abs_tol=1e-15)
        wrong=sorted([(NAMES[j] if j<5 else 'Abstain',int(cm[c,j])) for j in range(6) if j!=c and cm[c,j]],key=lambda x:-x[1])
        rows.append({'class':c,'class_name':NAMES[c],'model':model,**pc,'true_positives':tp,'false_positives':fp,'false_negatives':fn,'hardware_recall_ge_0.90':('PASS' if pc['recall']>=.9 else 'FAIL') if c in [1,2,3] else 'N/A','confusion_destinations':'; '.join(f'{name}: {count}' for name,count in wrong) or 'None'})
        for j in range(6):confusions.append({'model':model,'true_class':c,'true_state':NAMES[c],'predicted_class':j if j<5 else 'abstain','predicted_state':NAMES[j] if j<5 else 'Abstain','count':int(cm[c,j]),'row_fraction':d['row_normalized_confusion_matrix'][c][j]})
    for field,src in [('test_macro_f1','macro_f1'),('test_weighted_f1','weighted_f1'),('test_macro_AP','macro_AP'),('test_hardware_macro_recall','hardware_macro_recall')]:assert math.isclose(float(overall[key][field]),d[src],abs_tol=1e-15)
    assert math.isclose(sum(d['per_class'][str(c)]['f1'] for c in range(5))/5,d['macro_f1'],abs_tol=1e-15)
    assert math.isclose(sum(d['per_class'][str(c)]['f1']*supports[c] for c in range(5))/146461,d['weighted_f1'],abs_tol=1e-15)
    for field in ['threshold','precision','recall','f1','normal_false_alarm_rate','shade_false_alarm_rate','combined_nonhardware_FPR','TP','FP','FN']:
        assert math.isclose(float(alerts[key][field]),d['hardware_alert_metrics'][field],abs_tol=1e-15)
assert data['LightGBM__E4']['confusion_matrix'][1]==[0,1179,453,0,729,0]
def write_csv(name,values):
    with (OUT/name).open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(values[0]));w.writeheader();w.writerows(values)
rows.sort(key=lambda r:(r['class'],MODELS.index(r['model'])))
write_csv('RF_vs_LightGBM_Class_Metrics.csv',rows)
write_csv('RF_vs_LightGBM_Confusion_Counts.csv',confusions)
specs=[('Macro-F1','test_macro_f1','score','TEST',True),('Weighted-F1','test_weighted_f1','score','TEST',True),('Macro AP','test_macro_AP','score','TEST',True),('Hardware macro recall','test_hardware_macro_recall','score','TEST',True),('Hardware alert precision','test_alert_precision','score','TEST',True),('Hardware alert recall','test_alert_recall','score','TEST',True),('Hardware alert F1','test_alert_F1','score','TEST',True),('Hardware alert AP','test_alert_AP','score','TEST',True),('Normal FPR','test_normal_FPR','percent','TEST',False),('Shade FPR','test_shade_FPR','percent','TEST',False),('Combined FPR','test_combined_FPR','percent','TEST',False),('p95 latency','validation_p95_ms','ms','VALIDATION block 13',False),('Artifact size','artifact_MiB','MiB','TRAIN-fitted artifact',False),('Dropout macro-F1 loss','validation_dropout_loss','score','VALIDATION frozen 1% dropout',False),('Physical channels','physical_channels','channels','E4 configuration',False)]
sysrows=[]
for title,field,unit,pop,higher in specs:
    vals=[float(overall[k][field]) for k in KEYS]
    winner='Tie' if vals[0]==vals[1] else MODELS[int(vals[1]>vals[0]) if higher else int(vals[1]<vals[0])]
    sysrows.append({'metric':title,'RF E4':vals[0]*100 if unit=='percent' else vals[0],'LightGBM E4':vals[1]*100 if unit=='percent' else vals[1],'unit':unit,'population':pop,'higher_is_better':higher,'better_on_this_metric':winner})
write_csv('RF_vs_LightGBM_System_Metrics.csv',sysrows)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':300})
def save(fig,name):
    fig.savefig(FIG/(name+'.png'),bbox_inches='tight');fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
for field,name,label in [('recall','rf_vs_lgbm_class_recall','Recall'),('f1','rf_vs_lgbm_class_f1','F1-score')]:
    fig,ax=plt.subplots(figsize=(11,5));x=np.arange(5);w=.36
    for i,(key,model,color) in enumerate(zip(KEYS,MODELS,COLORS)):
        values=[data[key]['per_class'][str(c)][field] for c in range(5)]
        bars=ax.bar(x+(i-.5)*w,values,w,label=model,color=color)
        ax.bar_label(bars,labels=[f'{v:.4f}' for v in values],padding=4,fontsize=9)
    if field=='recall':ax.hlines(.90,.58,3.42,colors='#a21f25',linestyles='--',linewidth=1.7,label='0.90 requirement: hardware classes 1–3 only')
    ax.set_xticks(x,['Normal','Short Circuit','Resistive\nDegradation','Open Circuit','Building Shade']);ax.set_ylim(0,1.17);ax.set_ylabel(label)
    ax.set_title(f'Frozen TEST: sparse four-channel models — per-class {label.lower()}\nN = 146,461; Building Shade is an environmental state',pad=14)
    ax.legend(loc='lower left',fontsize=9);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True);fig.tight_layout();save(fig,name)
fig,axes=plt.subplots(1,2,figsize=(16,6.1),sharey=True)
for ax,key,model in zip(axes,KEYS,MODELS):
    cm=np.array(data[key]['confusion_matrix']);norm=np.array(data[key]['row_normalized_confusion_matrix'])
    im=ax.imshow(norm,cmap='Blues',vmin=0,vmax=1,aspect='equal')
    for i in range(5):
        for j in range(6):ax.text(j,i,f'{norm[i,j]*100:.3f}%\n(n={cm[i,j]:,})',ha='center',va='center',fontsize=8,color='white' if norm[i,j]>.6 else 'black')
    ax.set_xticks(range(6),['Normal','Short\nCircuit','Degradation','Open\nCircuit','Building\nShade','Abstain'],rotation=35,ha='right')
    ax.set_yticks(range(5),['Normal','Short Circuit','Degradation','Open Circuit','Building Shade']);ax.set_title(model);ax.set_xlabel('Predicted state')
axes[0].set_ylabel('True state');fig.suptitle('Frozen TEST confusion matrices: row-normalized percentages and unchanged counts\nEach true-class row totals 100%; zero abstentions; N = 146,461',y=.98)
fig.subplots_adjust(left=.10,right=.92,bottom=.23,top=.83,wspace=.13);cax=fig.add_axes([.94,.25,.012,.55]);fig.colorbar(im,cax=cax,label='Fraction of true class');save(fig,'rf_vs_lgbm_confusion_normalized')
fig,axes=plt.subplots(1,2,figsize=(10,4.8))
for ax,field,title,unit,limit in zip(axes,['validation_p95_ms','artifact_MiB'],['Single-observation p95 latency','Complete fitted artifact'],['ms','MiB'],[10,10]):
    vals=[float(overall[k][field]) for k in KEYS];bars=ax.bar(MODELS,vals,color=COLORS,width=.55)
    ax.bar_label(bars,labels=[f'{v:.2f}' if unit=='ms' else f'{v:.4f}' for v in vals],padding=4);ax.axhline(limit,color='#a21f25',ls='--',label=f'Target ≤ {limit} {unit}');ax.set_ylim(0,max(vals+[limit])*1.25);ax.set_ylabel(unit);ax.set_title(title);ax.legend(loc='upper right',fontsize=8)
fig.suptitle('Frozen engineering evidence — distinct axes and populations\nLatency: VALIDATION block 13; artifact: TRAIN-fitted wrapper/pipeline',fontsize=11);fig.tight_layout();save(fig,'rf_vs_lgbm_resources')
def table(headers,values):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in values])
primary=table(['Class','Model','Precision','Recall','F1','AP','Support','Hardware recall ≥0.90?'],[[f"{r['class']} — {r['class_name']}",r['model'],*[f"{r[f]:.4f}" for f in ['precision','recall','f1','AP']],f"{r['support']:,}",r['hardware_recall_ge_0.90']] for r in rows])
counts=table(['Class','Model','TP','FP','FN','Wrong prediction destinations'],[[r['class_name'],r['model'],r['true_positives'],r['false_positives'],r['false_negatives'],r['confusion_destinations']] for r in rows])
systemtable=table(['Metric','RF E4','LightGBM E4','Better on this metric / interpretation'],[[r['metric'],f"{r['RF E4']:.6f}" if r['metric']=='Dropout macro-F1 loss' else f"{r['RF E4']:.2f}" if r['unit']=='ms' else str(int(r['RF E4'])) if r['unit']=='channels' else f"{r['RF E4']:.4f}"+('%' if r['unit']=='percent' else ''),f"{r['LightGBM E4']:.6f}" if r['metric']=='Dropout macro-F1 loss' else f"{r['LightGBM E4']:.2f}" if r['unit']=='ms' else str(int(r['LightGBM E4'])) if r['unit']=='channels' else f"{r['LightGBM E4']:.4f}"+('%' if r['unit']=='percent' else ''),r['better_on_this_metric']] for r in sysrows])
prefs=[
('Normal','LightGBM has higher precision, recall, F1 and AP. Prefer LightGBM for identifying normal operation. RF sends 6,604 normal observations to Building Shade versus 425 for LightGBM. These errors reduce normal recall but are not hardware diagnoses. The five-class hardware assignments from normal are 22 for RF versus 8 for LightGBM; separately thresholded alert false positives are 20 versus 11.'),
('Short Circuit','RF has higher precision, recall, F1 and AP. Prefer RF decisively for short-circuit identification. RF correctly identifies 2,360/2,361 and mislabels one as shade. LightGBM identifies only 1,179/2,361; 729 go to Building Shade and 453 to Resistive Degradation. Those 1,182 misses account for about half the true short-circuit class. RF PASS; LightGBM FAIL for the predeclared recall requirement.'),
('Resistive Degradation','RF has higher precision, F1 and AP; LightGBM has slightly higher recall (0.9929515419 versus 0.9907488987). Prefer RF for balanced degradation identification and fewer false degradation diagnoses, while LightGBM has the sensitivity advantage. RF has 50 false positives and 21 false negatives; LightGBM has 496 false positives and 16 false negatives. Most LightGBM false degradation diagnoses include the 453 true short-circuit observations. Both PASS recall ≥0.90. RF misses go to short circuit (15) and normal (6); LightGBM misses go to short circuit (11) and shade (5).'),
('Open Circuit','LightGBM has slightly higher precision; RF has higher recall, F1 and AP. The F1 scores are practically tied: RF 0.998963730570 versus LightGBM 0.998962870774 (difference about 8.60×10⁻⁷). Both display 0.9990 at four decimals. RF has no open-circuit misses and five false positives (all from shade); LightGBM misses two open circuits as degradation and has three false positives (all from shade). Prefer RF if avoiding missed open circuits is primary; LightGBM if minimizing false open-circuit diagnoses is primary. Both PASS. No meaningful statistical superiority is established by these tiny differences.'),
('Building Shade','LightGBM has higher precision, recall, F1 and AP. Prefer LightGBM for this environmental state. RF shade precision is reduced by 6,604 normal observations incorrectly assigned shade; LightGBM assigns 425 normal and 729 short circuits to shade. RF misses 132 shade observations: 103 to hardware classes and 29 to normal. LightGBM misses 94: 79 to hardware classes and 15 to normal. The hardware recall requirement is N/A for shade; shade is not a hardware fault.')]
interpret='\n\n'.join('### Class '+str(i)+' — '+name+'\n\n'+s for i,(name,s) in enumerate(prefs))
resource=table(['Requirement','RF E4','LightGBM E4'],[['Each hardware class recall ≥0.90','PASS / PASS / PASS (classes 1/2/3)','FAIL / PASS / PASS (classes 1/2/3)'],['p95 ≤10 ms','FAIL: 36.81 ms','PASS: 6.12 ms'],['Artifact ≤10 MiB','FAIL: 11.6654 MiB','PASS: 1.5692 MiB'],['1% dropout loss ≤0.05','PASS: 0.008163','PASS: 0.010639'],['Physical channels ≤4','PASS: 4','PASS: 4']])
normal_pct=124512/146461*100;short_pct=2361/146461*100
report=f'''# RF E4 versus LightGBM E4: frozen class-by-class comparison

Source commit: `{COMMIT}`. Both candidates use E4 = [vdc1, vdc2, idc1, idc2], four physical channels. RF has 8 mathematical inputs; LightGBM has 13 because approved derivatives and availability indicators do not add measured channels. This comparison uses frozen TEST evidence, with explicitly labeled frozen VALIDATION/TRAIN resource evidence. No report is modified.

## Class-level metrics

All metrics below are observation-level TEST values. AP is frozen one-vs-rest average precision, not trapezoidal PR integration. Precision/recall/F1/AP are displayed to four decimals; CSV files retain full precision. Supports are identical between models, not additive across models. The recall criterion applies only to hardware classes H = {{1,2,3}}. Building Shade is environmental.

{primary}

![Per-class recall](figures/rf_vs_lgbm_class_recall.png)

![Per-class F1](figures/rf_vs_lgbm_class_f1.png)

## Error counts and destinations

FP and FN are transparently derived by summing the frozen 5×6 confusion matrices, including the abstention column. No prediction is regenerated. Both candidates have zero abstentions on this reference test. Class FP counts all other true classes assigned this class; it is distinct from binary hardware-alert FP.

{counts}

![Normalized confusion matrices with original counts](figures/rf_vs_lgbm_confusion_normalized.png)

## Interpretation for each class

{interpret}

## System-level comparison

The table compares the numeric direction for each metric; it does not designate a universal winner. FPRs are percentages. p95 is ms; artifact size is MiB. Dropout losses are differences in macro-F1, not percentages.

{systemtable}

### Five-class classification and imbalance

RF E4 provides the stronger sparse fault-type classification performance among the evaluated configurations: macro-F1 0.9505 versus 0.9021 and hardware macro recall 0.9968 versus 0.8305. It meets the individual recall requirement for all three hardware states. LightGBM is stronger on Normal and Building Shade, but fails short-circuit recall.

Normal comprises {normal_pct:.2f}% of TEST (124,512/146,461); Short Circuit comprises only {short_pct:.2f}% (2,361/146,461). Weighted-F1 weights each class F1 by support. LightGBM's near-perfect normal performance and strong shade performance therefore dominate its weighted-F1 of 0.9872, despite short-circuit recall 0.4994 and F1 0.6561. RF's 6,604 normal-to-shade confusions weigh heavily against its weighted-F1. Macro-F1 gives each class equal weight and exposes minority-class weakness. High AP assesses score ranking over thresholds; it does not guarantee strong recall for the fixed argmax class decision. No probability calibration is inferred. No paired significance or independent-site superiority is claimed.

### Binary hardware alerting — a separate decision

The frozen score is s_H = p1+p2+p3. Thresholds remain RF 0.5913558658757772 and LightGBM 0.13860002397413157, selected on VALIDATION block 14, not TEST. Combined FPR uses Normal + Building Shade as negatives. Alert AP uses the hardware score, not five-class AP.

LightGBM has slightly higher aggregate alert recall, F1 and AP; RF has slightly higher alert precision and lower shade/combined FPR. LightGBM has lower normal FPR. Thus binary alert performance is comparable and the preferred metric depends on the cost of misses versus false alarms. Frozen alert counts: RF TP=7,009, FP=116, FN=32; LightGBM TP=7,019, FP=117, FN=22. Both combined FPRs meet 1%. These are descriptive differences on this partition, not a universal performance ranking.

A true Short Circuit predicted Resistive Degradation is wrong for five-class classification but can still yield a correct hardware alert. A shade argmax can also coexist with a summed hardware probability above the frozen threshold. LightGBM's frozen class-1 *alert* recall is {data['LightGBM__E4']['hardware_alert_metrics']['hardware_class_alert_recall']['1']:.4f}, versus class-1 *classification* recall 0.4994; RF class-1 alert recall is {data['RF__E4']['hardware_alert_metrics']['hardware_class_alert_recall']['1']:.4f}. Excellent aggregate alerting therefore does not establish reliable fault-subtype diagnosis. The saved aggregate evidence does not link each confusion destination to alert outcomes; no such joint counts are invented.

For Normal, five-class hardware assignments are RF 22/124,512 (0.0177%) versus LightGBM 8/124,512 (0.0064%); frozen thresholded alert FPR is instead 0.0161% versus 0.0088%. For Building Shade, five-class hardware assignments are RF 103/14,908 (0.6909%) versus LightGBM 79/14,908 (0.5299%); thresholded shade-alert FPR is instead 0.6439% versus 0.7110%. The differing order for shade demonstrates why argmax confusions cannot substitute for thresholded alert evaluation.

### Resources and robustness

{resource}

![Resource comparison on separate axes](figures/rf_vs_lgbm_resources.png)

LightGBM provides the stronger computational profile: approximately six times lower p95 and 7.4 times smaller fitted artifact on the recorded host/protocol. RF has the smaller frozen isolated-dropout macro-F1 loss, although both pass. These latency/robustness values are VALIDATION evidence; fitted size describes the TRAIN-fitted complete wrapper/pipeline. They are not new TEST experiments or field-device guarantees. The frozen benchmark used 100 warmups and 2,000 single-observation calls. No causal sensor-importance or universal sensor-redundancy conclusion follows.

No evaluated configuration satisfied all predeclared engineering criteria. RF fails latency and size; LightGBM fails short-circuit classification recall. Four physical channels do not make either configuration accepted under all criteria.

## Evidence and limitations

All source files were verified against Git blobs at the exact authoritative commit before use:

'''+'\n'.join(f'- `{p}` — SHA-256 `{h["sha256"]}`.' for p,h in evidence.items())+'''

The final-candidate CSV supplies frozen resource/dropout values; the class CSV, detail JSON and alert CSV independently agree for both candidates. AP is preserved from the saved evidence and is not recomputed from absent ranking arrays. Error totals and normalization are arithmetic summaries of frozen counts. This analysis does not use the legacy 13-page report, LR F6 comparisons, model objects, fitting, model selection, new predictions, threshold tuning, or data-driven criterion changes.

The test partition had prior legacy exposure, contains dependent neighboring observations from one installation, and lacks verifiable timestamps. No alerts-per-hour, independent-event reliability, causal attribution, external generalization, global optimality or statistical significance is inferred.

## Decision

- **Correct identification of the specific PV state/fault type:** prefer RF E4, particularly for short-circuit sensitivity and consistently high hardware-class recall; account for its resource failures and weaker normal/shade separation.
- **Resource-efficient hardware fault alerting:** prefer LightGBM E4, with competitive binary alert performance and passing resource targets; retain its explicit short-circuit diagnosis limitation. It is not accepted for the complete predeclared five-class engineering objective.

No final report was changed. No training/retraining, new predictions, commit, push or publication occurred. Review this separate package before any report integration.
'''
(OUT/'RF_vs_LightGBM_Class_Comparison.md').write_text(report,encoding='utf8')
for p in protected:assert hashlib.sha256(p.read_bytes()).hexdigest()==before[p.relative_to(ROOT).as_posix()]
audit={'commit':COMMIT,'test_rows':146461,'models':MODELS,'evidence':evidence,'class_metric_rows':len(rows),'system_metric_rows':len(sysrows),'confusion_cell_rows':len(confusions),'verified_short_circuit_LightGBM_destinations':{'Building Shade':729,'Resistive Degradation':453},'original_reports_unchanged':before,'predictions_generated':False,'models_fit':False,'thresholds_modified':False,'scope':'Frozen TEST classification/alert evidence; frozen VALIDATION latency/dropout and TRAIN-fitted artifact evidence explicitly labeled. FP/FN and plots derive only from frozen counts/metrics.','figures':'Four figures, each PNG and vector PDF.','files_created':sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file()),'existing_files_modified':[]}
audit['visual_review']='PASS: all four PNG plots inspected; labels/counts readable, no clipping; confusion normalization and zero abstentions verified; resource axes use separate units.'
audit['files_created']=sorted(set(audit['files_created']+['Comparison_Verification.json']))
(OUT/'Comparison_Verification.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
print(primary);print('\n'+counts);print('\n'+systemtable);print('\nComparison created and verified:',OUT)
