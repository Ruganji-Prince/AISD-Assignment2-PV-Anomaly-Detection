import {scenarioNames,generateScenario} from './scenarios.js';
import {labels,explanations} from './explanations.js';
const $=id=>document.getElementById(id);
const channels=['vdc1','vdc2','idc1','idc2'];
let source='synthetic', selected=0,seed=42,examples=[],busy=false,chart='voltage';
let currentSource='synthetic';
const icons=['check','bolt','resistance','disconnect','shade'];
const colors=['#1a9d78','#e05f56','#d89835','#8a65d2','#458bc1'];
function icon(element,name){element.querySelector('use').setAttribute('href','#icon-'+name);}
function measurements(){return Object.fromEntries(channels.map(k=>[k,$(k).value===''?null:Number($(k).value)]));}
function clearResult(){ $('result-content').hidden=true;$('result-empty').hidden=false;$('result-warnings').hidden=true;delete $('result-card').dataset.class;delete $('result-card').dataset.category;}
function clearError(){$('form-error').hidden=true;}
function showError(message){$('form-error').textContent=message;$('form-error').hidden=false;}
function sourceLabel(){return currentSource==='synthetic'?'Synthetic Demonstration Data':currentSource==='dataset'?'Historical Dataset Example':'Manual Measurements';}
function updateCharts(){
 const values=measurements(), keys=chart==='voltage'?['vdc1','vdc2']:['idc1','idc2'],unit=chart==='voltage'?'V':'A';
 const valid=keys.map(k=>Number.isFinite(values[k])&&values[k]>=0?values[k]:0);
 const maximum=Math.max(...valid,chart==='voltage'?400:10),tickMaximum=Math.ceil(maximum/(chart==='voltage'?100:2))*(chart==='voltage'?100:2);
 $('chart-heading').textContent=chart==='voltage'?'Channel voltage':'Channel current';$('chart-subtitle').textContent=`Comparison of supplied measurements (${unit})`;$('axis-label').textContent=chart==='voltage'?'Voltage (V)':'Current (A)';
 keys.forEach((key,j)=>{const node=$('bar'+(j+1));node.querySelector('.bar-fill').style.width=(valid[j]/tickMaximum*100)+'%';node.classList.toggle('zero',valid[j]/tickMaximum<.2);$('bar-value'+(j+1)).textContent=values[key]===null?'No value':`${valid[j].toFixed(chart==='voltage'?2:3)} ${unit}`;node.dataset.tooltip=`Channel ${j+1} | ${key}: ${values[key]===null?'not supplied':valid[j]+' '+unit} | ${sourceLabel()}`;node.setAttribute('aria-label',node.dataset.tooltip);});
 $('axis-ticks').replaceChildren(...Array.from({length:5},(_,i)=>{let x=document.createElement('span');x.textContent=Number((i/4*tickMaximum).toFixed(2));return x;}));
 $('chart-data-label').textContent=currentSource==='synthetic'?'Synthetic data':currentSource==='dataset'?'Dataset values':'Manual values';$('source-badge').textContent=sourceLabel();
}
function updateDiagram(){const k=selected;$('scenario-diagram').dataset.scenario=k===null?'manual':String(k);$('scenario-diagram').style.setProperty('--scenario-color',k===null?'#339a86':colors[k]);icon($('diagram-icon'),k===null?'chart':icons[k]);$('diagram-label').textContent=k===null?'Manual measurements':scenarioNames[k];$('diagram-source').textContent=k===null?'SCHEMATIC ONLY':'SELECTED INTENT';}
function applyScenario(){
 if(busy)return;
 const values=source==='synthetic'?generateScenario(selected,seed):examples.find(x=>x.id===selected)?.measurements;
 if(!values){showError('Dataset examples are unavailable. Choose Synthetic or enter measurements manually.');return;}
 for(const k of channels)$(k).value=values[k];currentSource=source;clearResult();clearError();updateCharts();updateDiagram();$('example-status').textContent=sourceLabel()+' loaded. Run inference for the actual prediction.';
}
function selectSource(next){
 if(busy)return;source=next;selected=0;seed=42;
 $('synthetic-tab').setAttribute('aria-selected',String(next==='synthetic'));$('dataset-tab').setAttribute('aria-selected',String(next==='dataset'));$('scenario-panel').setAttribute('aria-labelledby',next+'-tab');
 $('scenario-caption').textContent=next==='synthetic'?'Synthetic Demonstration Data':'Historical Dataset Examples';$('scenario-note').textContent=next==='synthetic'?'Illustrative patterns with small, seeded variations. Not validated fault simulations.':'Unmodified measurements from the released dataset. These observations are not synthetic.';
 $('load-example').hidden=next==='dataset';$('example-select').value='0';
 const panel=$('scenario-panel');panel.getAnimations().forEach(x=>x.cancel());if(!matchMedia('(prefers-reduced-motion:reduce)').matches)panel.animate([{opacity:.35},{opacity:1}],{duration:200});applyScenario();
}
function setBusy(value){busy=value;for(const id of [...channels,'predict-button','reset-button','load-example','example-select','synthetic-tab','dataset-tab'])$(id).disabled=value;$('loading-spinner').hidden=!value;$('button-icon').hidden=value;$('button-label').textContent=value?'Analyzing measurements...':'Run model inference';$('result-card').setAttribute('aria-busy',String(value));}
function renderResult(result){
 const k=result.predicted_class;if(!Number.isInteger(k)||!explanations[k])throw new Error('The service returned an invalid prediction.');
 const content=explanations[k];$('result-card').dataset.class=String(k);$('result-card').dataset.category=result.fault_category;
 $('predicted-label').textContent=labels[k];$('predicted-class').textContent='0'+k;$('category-badge').textContent=content.category;icon($('result-symbol'),content.symbol);
 $('meaning-text').textContent=content.meaning;$('cause-text').textContent=content.cause;$('check-text').textContent=content.check;
 const mismatch=selected!==null&&selected!==k;$('scenario-comparison').classList.toggle('mismatch',mismatch);
 $('scenario-comparison').textContent=selected===null?'Manual measurements | Actual model prediction shown.':`${sourceLabel()} | Selected: ${scenarioNames[selected]}. ${mismatch?'Prediction differs from selected intent.':'Prediction agrees with selected intent.'}`;
 $('result-warnings').textContent=(result.warnings||[]).join(' ');$('result-warnings').hidden=!(result.warnings||[]).length;$('result-empty').hidden=true;$('result-content').hidden=false;
 if(innerWidth<651)$('result-card').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth',block:'start'});
}
$('prediction-form').addEventListener('submit',async event=>{
 event.preventDefault();if(busy)return;clearError();const values=measurements();
 if(channels.some(k=>!Number.isFinite(values[k])||values[k]<0)){showError('Enter four finite, nonnegative numbers in volts and amperes.');return;}
 clearResult();setBusy(true);const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),60000);
 try{const response=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(values),signal:controller.signal});const result=await response.json();if(!response.ok)throw new Error(typeof result.detail==='string'?result.detail:'Unable to analyze these measurements.');renderResult(result);}
 catch(error){showError(error.name==='AbortError'?'The request timed out. Please try again.':error instanceof TypeError?'Unable to reach the prediction service. Please check the connection.':error.message);}
 finally{clearTimeout(timer);setBusy(false);}
});
$('example-select').addEventListener('change',()=>{selected=Number($('example-select').value);seed=42;applyScenario();});$('load-example').addEventListener('click',()=>{seed++;applyScenario();});$('synthetic-tab').addEventListener('click',()=>selectSource('synthetic'));$('dataset-tab').addEventListener('click',()=>selectSource('dataset'));
channels.forEach(k=>$(k).addEventListener('input',()=>{currentSource='manual';selected=null;clearResult();clearError();updateCharts();updateDiagram();}));
$('reset-button').addEventListener('click',()=>{if(busy)return;for(const k of channels)$(k).value='';currentSource='manual';selected=null;clearResult();clearError();updateCharts();updateDiagram();$('example-status').textContent='Measurements and result cleared.';});
for(const [id,kind] of [['voltage-tab','voltage'],['current-tab','current']])$(id).addEventListener('click',()=>{chart=kind;$('voltage-tab').setAttribute('aria-selected',String(kind==='voltage'));$('current-tab').setAttribute('aria-selected',String(kind==='current'));$('chart-panel').setAttribute('aria-labelledby',id);$('chart-tooltip').hidden=true;updateCharts();});
for(const id of ['bar1','bar2']){const node=$(id);const show=()=>{$('chart-tooltip').textContent=node.dataset.tooltip;$('chart-tooltip').hidden=false;};node.addEventListener('mouseenter',show);node.addEventListener('focus',show);node.addEventListener('click',show);node.addEventListener('mouseleave',()=>{$('chart-tooltip').hidden=true;});node.addEventListener('blur',()=>{$('chart-tooltip').hidden=true;});}
async function initialize(){
 scenarioNames.forEach((name,k)=>{const option=document.createElement('option');option.value=k;option.textContent=name;$('example-select').append(option);});applyScenario();
 try{const response=await fetch('/api/examples');if(!response.ok)throw new Error();examples=await response.json();}catch{$('dataset-tab').disabled=true;$('dataset-tab').title='Dataset examples unavailable';}
 try{const response=await fetch('/api/health');if(!response.ok)throw new Error();$('service-status').querySelector('span').textContent='Model ready';}catch{$('service-status').querySelector('span').textContent='Service unavailable';$('service-status').classList.add('unavailable');}
}
initialize();
