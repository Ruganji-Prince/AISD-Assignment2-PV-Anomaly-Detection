import {ensureReady,fetchExamples,requestPrediction,subscribeService,cancelServiceCheck} from './api.js';
import {scenarioNames,generateScenario} from './scenarios.js';
import {labels,explanations} from './explanations.js';
import {Replay,loadReplay} from './replay.js';
const $=id=>document.getElementById(id);
const channels=['vdc1','vdc2','idc1','idc2'];
let source='synthetic', selected=0,seed=42,examples=[],busy=false,chart='voltage';
let currentSource='synthetic';
let mode='manual',historicalSourceClass=null,currentPrediction=null,operation=0,activeRequest=null,startupController=null,recordedController=null,recordedData=null;
let hasPrediction=false,currentStep=0,navigating=false;
const visitedSteps=new Set([0]);
const icons=['check','bolt','resistance','disconnect','shade'];
const colors=['#087858','#b42318','#ad3c2f','#6b3fa0','#946000'];
function icon(element,name){element.querySelector('use').setAttribute('href','#icon-'+name);}
function measurements(){return Object.fromEntries(channels.map(k=>[k,$(k).value===''?null:Number($(k).value)]));}
function clearResult(){ const outdated=hasPrediction;hasPrediction=false;currentPrediction=null;$('view-assessment').hidden=true;$('prediction-status').textContent=outdated?'Measurements changed. Run inference again.':'Ready for inference.'; $('result-content').hidden=true;$('result-empty').hidden=false;$('result-warnings').hidden=true;delete $('step-3').dataset.class;delete $('step-3').dataset.category;}
function clearError(){$('form-error').hidden=true;}
function showError(message){$('form-error').textContent=message;$('form-error').hidden=false;$('prediction-status').textContent=message;}
function sourceLabel(){if(currentSource==='replay')return 'Historical TRAIN Replay';if(currentSource==='recorded')return 'Recorded TRAIN Observation';return currentSource==='synthetic'?'Synthetic Demonstration Data':currentSource==='dataset'?'Historical Dataset Example':'Manual Measurements';}
function updateCharts(){
 const values=measurements(), keys=chart==='voltage'?['vdc1','vdc2']:['idc1','idc2'],unit=chart==='voltage'?'V':'A';
 const valid=keys.map(k=>Number.isFinite(values[k])&&values[k]>=0?values[k]:0);
 const maximum=Math.max(...valid,chart==='voltage'?400:10),rounded=Math.ceil(maximum/(chart==='voltage'?100:2))*(chart==='voltage'?100:2),tickMaximum=Number.isFinite(rounded)?rounded:maximum;
 $('chart-heading').textContent=chart==='voltage'?'Channel voltage':'Channel current';$('chart-subtitle').textContent=`Comparison of supplied measurements (${unit})`;$('axis-label').textContent=chart==='voltage'?'Voltage (V)':'Current (A)';
 keys.forEach((key,j)=>{const node=$('bar'+(j+1));node.querySelector('.bar-fill').style.width=(valid[j]/tickMaximum*100)+'%';node.classList.toggle('zero',valid[j]/tickMaximum<.2);$('bar-value'+(j+1)).textContent=values[key]===null?'No value':`${valid[j].toFixed(chart==='voltage'?2:3)} ${unit}`;node.dataset.tooltip=`Channel ${j+1} | ${key}: ${values[key]===null?'not supplied':valid[j]+' '+unit} | ${sourceLabel()}`;node.setAttribute('aria-label',$('bar-value'+(j+1)).textContent+' | '+node.dataset.tooltip);});
 $('axis-ticks').replaceChildren(...Array.from({length:5},(_,i)=>{let x=document.createElement('span');x.textContent=Number((i/4*tickMaximum).toFixed(2));return x;}));
 $('chart-data-label').textContent=['replay','recorded'].includes(currentSource)?'Historical TRAIN values':currentSource==='synthetic'?'Synthetic data':currentSource==='dataset'?'Dataset values':'Manual values';$('source-badge').textContent=sourceLabel();
}
function updateDiagram(){const k=mode==='automatic'?currentPrediction:selected;$('scenario-diagram').dataset.scenario=k===null?'manual':String(k);$('scenario-diagram').style.setProperty('--scenario-color',k===null?'#339a86':colors[k]);icon($('diagram-icon'),k===null?'chart':icons[k]);$('diagram-label').textContent=k===null?(mode==='automatic'?'Awaiting model prediction':'Manual measurements'):scenarioNames[k];$('diagram-caption').textContent=mode==='automatic'?'Illustration of model output, not a confirmed diagnosis':k===null?'Input schematic, not a diagnosis':'Illustration of selected intent, not a diagnosis';$('diagram-source').textContent=mode==='automatic'?(k===null?'AWAITING MODEL':'MODEL PREDICTION'):k===null?'SCHEMATIC ONLY':'SELECTED INTENT';updateScenarioCards();}
function applyScenario(){
 if(busy||mode==='automatic')return;historicalSourceClass=null;$('recorded-select').value='';
 const values=source==='synthetic'?generateScenario(selected,seed):examples.find(x=>x.id===selected)?.measurements;
 if(!values){showError('Dataset examples are unavailable. Choose Synthetic or enter measurements manually.');return;}
 for(const k of channels)$(k).value=values[k];currentSource=source;clearResult();clearError();updateCharts();updateDiagram();$('example-status').textContent=sourceLabel()+' loaded. Run inference for the actual prediction.';
}
function selectSource(next){
 if(busy||mode==='automatic')return;source=next;selected=0;seed=42;
 $('synthetic-tab').setAttribute('aria-selected',String(next==='synthetic'));$('dataset-tab').setAttribute('aria-selected',String(next==='dataset'));$('scenario-panel').setAttribute('aria-labelledby',next+'-tab');
 $('scenario-caption').textContent=next==='synthetic'?'Synthetic Demonstration Data':'Historical Dataset Examples';$('scenario-note').textContent=next==='synthetic'?'Illustrative patterns with small, seeded variations. Not validated fault simulations.':'Unmodified measurements from the released dataset. These observations are not synthetic.';
 $('load-example').hidden=next==='dataset';$('example-select').value='0';
 const panel=$('scenario-panel');panel.getAnimations().forEach(x=>x.cancel());if(!matchMedia('(prefers-reduced-motion:reduce)').matches)panel.animate([{opacity:.35},{opacity:1}],{duration:200});applyScenario();
}
function setBusy(value){busy=value;document.querySelectorAll(".scenario-card").forEach(button=>button.disabled=value||mode==='automatic');for(const id of [...channels,'service-retry','predict-button','reset-button','load-example','example-select','synthetic-tab','dataset-tab','assessment-run'])$(id).disabled=value;$('loading-spinner').hidden=!value;$('button-icon').hidden=value;$('button-label').textContent=value?'Analyzing measurements...':'Run model inference';$('step-3').setAttribute('aria-busy',String(value));$('assessment-run').textContent=value?'Analyzing measurements...':'Run inference';if(value)$('prediction-status').textContent='Analyzing measurements...';
 if(mode==='automatic')for(const id of ['predict-button','reset-button','load-example','example-select','synthetic-tab','dataset-tab','assessment-run'])$(id).disabled=true;
 for(const k of channels)$(k).readOnly=mode==='automatic';$('load-recorded').disabled=value||mode==='automatic';$('recorded-select').disabled=value||mode==='automatic'||!recordedData;}
function renderResult(result){
 const k=result.predicted_class;if(!Number.isInteger(k)||!explanations[k])throw new Error('The service returned an invalid prediction.');
 const content=explanations[k];$('step-3').dataset.class=String(k);$('step-3').dataset.category=result.fault_category;
 $('predicted-label').textContent=labels[k];$('predicted-class').textContent='0'+k;$('category-badge').textContent=content.category;icon($('result-symbol'),content.symbol);
 $('meaning-text').textContent=content.meaning;$('cause-text').textContent=content.cause;$('check-text').textContent=content.check;
 const reference=['replay','recorded'].includes(currentSource)?historicalSourceClass:selected;const mismatch=reference!==null&&reference!==k;$('scenario-comparison').classList.toggle('mismatch',mismatch);
 $('scenario-comparison').textContent=['replay','recorded'].includes(currentSource)?`Source label: ${labels[historicalSourceClass]}. Model prediction: ${labels[k]}. ${mismatch?'Disagrees with source label.':'Agrees with source label.'}`:selected===null?'Manual measurements | Actual model prediction shown.':`${sourceLabel()} | Selected: ${scenarioNames[selected]}. ${mismatch?'Prediction differs from selected intent.':'Prediction agrees with selected intent.'}`;
 $('result-warnings').textContent=(result.warnings||[]).join(' ');$('result-warnings').hidden=!(result.warnings||[]).length;$('result-empty').hidden=true;$('result-content').hidden=false;
 hasPrediction=true;currentPrediction=k;updateDiagram();$('view-assessment').hidden=false;$('prediction-status').textContent='Prediction ready. Open Model Assessment to view the result.';
}
$('prediction-form').addEventListener('submit',async event=>{
 event.preventDefault();if(busy||mode==='automatic')return;clearError();const values=measurements();
 if(channels.some(k=>!Number.isFinite(values[k])||values[k]<0)){showError('Enter four finite, nonnegative numbers in volts and amperes.');await goToStep(0);$('prediction-form').reportValidity();return;}
 clearResult();setBusy(true);const token=++operation;activeRequest=new AbortController();
 try{const result=await requestPrediction(values,{signal:activeRequest.signal});if(token===operation&&mode==='manual')renderResult(result);}
 catch(error){if(token!==operation)return;showError(error.name==='AbortError'?'The request timed out. Please try again.':error instanceof TypeError?'Unable to reach the prediction service. Please check the connection.':error.message);}
 finally{if(token===operation){activeRequest=null;setBusy(false);if(!$('form-error').hidden&&currentStep!==0)await goToStep(0);}}
});
$('example-select').addEventListener('change',()=>{selected=Number($('example-select').value);seed=42;applyScenario();});$('load-example').addEventListener('click',()=>{seed++;applyScenario();});$('synthetic-tab').addEventListener('click',()=>selectSource('synthetic'));$('dataset-tab').addEventListener('click',()=>selectSource('dataset'));
channels.forEach(k=>$(k).addEventListener('input',()=>{$('recorded-select').value='';$('recorded-note').textContent='Manual measurements. A previously selected source label no longer applies.';currentSource='manual';selected=null;historicalSourceClass=null;clearResult();clearError();updateCharts();updateDiagram();}));
$('reset-button').addEventListener('click',()=>{if(busy)return;$('recorded-select').value='';$('recorded-note').textContent='Measurements cleared. Choose an optional observation or enter values manually.';for(const k of channels)$(k).value='';currentSource='manual';selected=null;historicalSourceClass=null;clearResult();clearError();updateCharts();updateDiagram();$('example-status').textContent='Measurements and result cleared.';});
for(const [id,kind] of [['voltage-tab','voltage'],['current-tab','current']])$(id).addEventListener('click',()=>{chart=kind;$('voltage-tab').setAttribute('aria-selected',String(kind==='voltage'));$('current-tab').setAttribute('aria-selected',String(kind==='current'));$('chart-panel').setAttribute('aria-labelledby',id);$('chart-tooltip').hidden=true;updateCharts();});
for(const id of ['bar1','bar2']){const node=$(id);const show=()=>{$('chart-tooltip').textContent=node.dataset.tooltip;$('chart-tooltip').hidden=false;};node.addEventListener('mouseenter',show);node.addEventListener('focus',show);node.addEventListener('click',show);node.addEventListener('mouseleave',()=>{$('chart-tooltip').hidden=true;});node.addEventListener('blur',()=>{$('chart-tooltip').hidden=true;});}
// Presentation-only shortcuts reuse the existing selector and its state transition.
function updateScenarioCards(){
 document.querySelectorAll('.scenario-card').forEach((button,k)=>{
  button.setAttribute('aria-pressed',String(selected===k));
  button.querySelector('.scenario-card-source').textContent=source==='dataset'?'Reference observation':'Illustrative synthetic intent';
 });
}
function createScenarioCards(){
 scenarioNames.forEach((name,k)=>{
  const button=document.createElement('button');button.type='button';button.className='scenario-card';
  const symbol=document.createElementNS('http://www.w3.org/2000/svg','svg');symbol.setAttribute('aria-hidden','true');
  const use=document.createElementNS('http://www.w3.org/2000/svg','use');use.setAttribute('href','#icon-'+icons[k]);symbol.append(use);
  const title=document.createElement('strong');title.textContent=name;
  const kind=document.createElement('span');kind.className='scenario-card-source';
  const action=document.createElement('span');action.className='scenario-card-action';action.textContent='Select scenario';
  button.append(symbol,title,kind,action);button.addEventListener('click',()=>{if(busy)return;$('example-select').value=String(k);$('example-select').dispatchEvent(new Event('change'));});
  $('scenario-cards').append(button);
 });
}
async function initialize(){
 scenarioNames.forEach((name,k)=>{const option=document.createElement('option');option.value=k;option.textContent=name;$('example-select').append(option);});createScenarioCards();applyScenario();
 try{startupController=new AbortController();await ensureReady({signal:startupController.signal});if(startupController.signal.aborted)return;examples=await fetchExamples({signal:startupController.signal});$('dataset-tab').disabled=mode==='automatic';}catch{$('dataset-tab').disabled=true;$('dataset-tab').title='Connect to the cloud service to load dataset examples.';}

}
subscribeService((name,message)=>{
 const node=$('service-status');node.dataset.state=name;node.classList.toggle('unavailable',name==='unavailable');node.querySelector('span').textContent=message;
 $('service-retry').hidden=name!=='unavailable';$('service-retry').disabled=busy;
});
$('service-retry').addEventListener('click',async()=>{if(busy||mode==='automatic')return;try{await ensureReady({force:true});examples=await fetchExamples();$('dataset-tab').disabled=false;clearError();}catch(error){showError(error.message);}});
initialize();

function clearReplayPrediction(){
 clearResult();$('replay-prediction').textContent='Not evaluated';$('replay-agreement').textContent='Not evaluated';$('replay-interpretation').textContent='No current prediction. Run or resume inference.';setBusy(false);updateDiagram();
}
const replay=new Replay({
 ready:signal=>ensureReady({signal}),infer:(values,signal)=>{setBusy(true);return requestPrediction(values,{signal});},
 onObservation:(row,count)=>{historicalSourceClass=row.source_class;selected=null;currentSource='replay';clearResult();clearError();for(const k of channels){$(k).value=row.measurements[k];$('replay-'+k).textContent=String(row.measurements[k])+(k.startsWith('v')?' V':' A');}$('replay-counter').textContent=count;$('replay-source').textContent=labels[row.source_class];$('replay-prediction').textContent='Awaiting Azure';$('replay-agreement').textContent='Not evaluated';$('replay-interpretation').textContent='Waiting for the actual model response.';updateCharts();updateDiagram();},
 onResult:(result,row)=>{renderResult(result);$('replay-prediction').textContent=labels[result.predicted_class];$('replay-agreement').textContent=result.predicted_class===row.source_class?'Agrees with source label':'Disagrees with source label';$('replay-interpretation').textContent=explanations[result.predicted_class].meaning;setBusy(false);},
 onCancel:clearReplayPrediction,
 onState:(state,message,count)=>{$('replay-panel').dataset.state=state;$('replay-status').textContent=message;if(state!=='paused')$('replay-counter').textContent=count;$('replay-start').disabled=['starting','predicting','waiting','completed'].includes(state);$('replay-pause').disabled=!['starting','predicting','waiting'].includes(state);if(state==='error'){showError(message);setBusy(false);}}
});
function setMode(next){
 if(next===mode)return;
 operation++;activeRequest?.abort();activeRequest=null;startupController?.abort();recordedController?.abort();cancelServiceCheck();replay.reset();
 mode=next;historicalSourceClass=null;currentSource='manual';selected=null;clearResult();clearError();
 $('mode-auto').setAttribute('aria-pressed',String(next==='automatic'));$('mode-manual').setAttribute('aria-pressed',String(next==='manual'));$('replay-panel').hidden=next!=='automatic';$('manual-examples').hidden=next==='automatic';$('recorded-select').value='';
 $('replay-source').textContent='Not selected';$('replay-prediction').textContent='Not evaluated';$('replay-agreement').textContent='Not evaluated';setBusy(false);updateCharts();updateDiagram();
}
$('mode-auto').addEventListener('click',()=>setMode('automatic'));
$('mode-manual').addEventListener('click',()=>setMode('manual'));
$('replay-start').addEventListener('click',()=>{if(mode==='automatic'&&!document.hidden)void replay.start();});
$('replay-pause').addEventListener('click',()=>replay.pause());
$('replay-restart').addEventListener('click',()=>{if(mode==='automatic'&&!document.hidden)void replay.restart();});
document.addEventListener('visibilitychange',()=>{if(document.hidden){startupController?.abort();recordedController?.abort();cancelServiceCheck();if(activeRequest){operation++;activeRequest.abort();activeRequest=null;clearResult();setBusy(false);}if(mode==='automatic')replay.pause('Paused because this tab is hidden. Press Start to resume.');}});
$('load-recorded').addEventListener('click',async()=>{
 if(busy||mode!=='manual')return;$('load-recorded').disabled=true;const controller=new AbortController();recordedController=controller;
 try{const loaded=await loadReplay(controller.signal);if(mode!=='manual'||controller.signal.aborted||recordedController!==controller)return;recordedData=loaded;
  const select=$('recorded-select');while(select.options.length>1)select.remove(1);
  for(let k=0;k<5;k++){const group=document.createElement('optgroup');group.label=labels[k];let count=0;recordedData.observations.forEach((row,i)=>{if(row.source_class===k){const option=document.createElement('option');option.value=String(i);option.textContent=`${labels[k]} ? observation ${++count}`;group.append(option);}});select.append(group);}select.disabled=false;$('recorded-note').textContent='150 recorded TRAIN observations loaded. Choose one to fill inputs; then run inference.';
 }catch(error){if(!controller.signal.aborted&&recordedController===controller)showError(error.message);}finally{if(mode==='manual'&&recordedController===controller)$('load-recorded').disabled=false;}
});
$('recorded-select').addEventListener('change',()=>{
 const value=$('recorded-select').value;if(value===''||busy||mode!=='manual')return;const row=recordedData.observations[Number(value)];
 historicalSourceClass=row.source_class;selected=null;currentSource='recorded';for(const k of channels)$(k).value=row.measurements[k];clearResult();clearError();updateCharts();updateDiagram();$('recorded-note').textContent=`Source label: ${labels[row.source_class]}. Inputs filled only; run inference for the actual model prediction.`;
});

function syncNavigation(){
 document.querySelectorAll('.step-tab').forEach((button,i)=>{
  const state=i===currentStep?'current':visitedSteps.has(i)?'completed':'unvisited';button.dataset.state=state;
  if(i===currentStep)button.setAttribute('aria-current','step');else button.removeAttribute('aria-current');
  button.querySelector('.step-state').textContent=state==='current'?'Current':state==='completed'?'Completed':'Not visited';
  button.removeAttribute('aria-label'); // Visible number, label and state provide the complete accessible name.
 });
}
async function goToStep(target,focusHeading=true){
 if(!Number.isInteger(target)||target<0||target>3||target===currentStep||navigating)return;
 navigating=true;const old=$('step-'+currentStep),next=$('step-'+target),direction=target>currentStep?1:-1;
 const duration=matchMedia('(prefers-reduced-motion:reduce)').matches?0:125;
 $('chart-tooltip').hidden=true;
 if(duration)await old.animate([{opacity:1,transform:'translateX(0)'},{opacity:0,transform:`translateX(${-direction*10}px)`}],{duration,easing:'ease-in'}).finished;
 old.hidden=true;next.hidden=false;currentStep=target;visitedSteps.add(target);syncNavigation();
 $('step-announcement').textContent=`Step ${target+1} of 4: ${['PV Measurements','PV Scenarios','Graphical Analysis','Model Assessment'][target]}`;
 if(duration)await next.animate([{opacity:0,transform:`translateX(${direction*10}px)`},{opacity:1,transform:'translateX(0)'}],{duration,easing:'ease-out'}).finished;
 navigating=false;if(focusHeading)$('step-heading-'+target).focus({preventScroll:true});
 if(innerWidth<651)$('workflow').scrollIntoView({block:'start',behavior:'instant'});
}
document.querySelectorAll('[data-go-step]').forEach(button=>button.addEventListener('click',()=>goToStep(Number(button.dataset.goStep))));
document.querySelectorAll('.step-tab').forEach((button,i)=>{
 button.addEventListener('click',()=>goToStep(i));
 button.addEventListener('keydown',event=>{let target;if(event.key==='ArrowRight')target=Math.min(i+1,3);else if(event.key==='ArrowLeft')target=Math.max(i-1,0);else if(event.key==='Home')target=0;else if(event.key==='End')target=3;else return;event.preventDefault();$('step-tab-'+target).focus();goToStep(target,false);});
});
$('view-assessment').addEventListener('click',()=>goToStep(3));
$('assessment-run').addEventListener('click',async()=>{const form=$('prediction-form');if(!form.checkValidity()){await goToStep(0);form.reportValidity();return;}form.requestSubmit();});
syncNavigation();
