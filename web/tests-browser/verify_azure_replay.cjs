// Bounded built-frontend -> existing production Azure API checks. No proxy/mocked successes.
const{chromium}=require('playwright');const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),base=process.env.PV_APP_URL||'http://127.0.0.1:8080',api='https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io';
const output=process.env.PV_EVIDENCE_DIR;if(!output)throw new Error('PV_EVIDENCE_DIR required');
const cases=JSON.parse(fs.readFileSync(path.join(root,'deployment/example_cases.json'))),proof=JSON.parse(fs.readFileSync(path.join(root,'technical_evaluation/PV_Replay_Verification.json'))),data=JSON.parse(fs.readFileSync(path.join(root,'web/data/pv_historical_replay.json')));
const labels=['Normal','Short Circuit','Resistive Degradation','Open Circuit','Natural Building Shade'],keys=['vdc1','vdc2','idc1','idc2'];
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn,limit=15000){const deadline=Date.now()+limit;while(Date.now()<deadline){if(await fn())return;await pause(25);}throw new Error('Live browser condition timed out.');}
function luminance(rgb){const a=rgb.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;});return a[0]*.2126+a[1]*.7152+a[2]*.0722;}
function contrast(a,b){const x=[luminance(a),luminance(b)].sort((a,b)=>a-b);return(x[1]+.05)/(x[0]+.05);}
(async()=>{
 const browser=await chromium.launch({headless:true});try{
 const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const requests=[],manual=[],automatic=[],contrasts=[];let phase='manual',active=0,maxActive=0,health;
 page.on('request',r=>{if(r.url()===api+'/api/predict'&&r.method()==='POST'){active++;maxActive=Math.max(maxActive,active);const values=r.postDataJSON();assert.deepEqual(Object.keys(values),keys);requests.push({phase,input:values,start_ms:performance.now(),request:r});}});
 page.on('response',async r=>{if(r.url()===api+'/api/predict'&&r.request().method()==='POST'){try{await r.finished();}finally{active--;const row=requests.find(v=>v.request===r.request());if(row)row.finish_ms=performance.now();}}});
 const healthResponse=page.waitForResponse(r=>r.url()===api+'/api/health',{timeout:130000});await page.goto(base,{waitUntil:'domcontentloaded'});
 health=await(await healthResponse).json();assert.equal(health.model_sha256,proof.model_sha256);await until(()=>page.$eval('#service-status',n=>n.dataset.state==='ready'),130000);
 assert.equal(await page.getAttribute('#mode-manual','aria-pressed'),'true');
 const manualCheckpoint=path.join(output,'Azure_Manual_Checkpoint.json');
 if(fs.existsSync(manualCheckpoint)){const saved=JSON.parse(fs.readFileSync(manualCheckpoint));assert.equal(saved.status,'PASS');manual.push(...saved.manual_reference_cases);console.log('REUSING_VERIFIED_FIVE_MANUAL_CASES');}
 else for(const c of cases){
  for(const[k,v]of Object.entries(c.input))await page.fill('#'+k,String(v));const pending=page.waitForResponse(r=>r.url()===api+'/api/predict'&&r.request().method()==='POST');await page.click('#predict-button');const response=await pending;assert.equal(response.status(),200);const result=await response.json();
  for(const[k,v]of Object.entries(c.output))assert.deepEqual(result[k],v);await until(()=>page.$eval('#result-content',n=>!n.hidden));await page.click('#view-assessment');await until(()=>page.$eval('#step-3',n=>!n.hidden));assert.equal(await page.textContent('#predicted-label'),labels[c.case]);
  const category=await page.$eval('#category-badge',n=>({text:n.textContent,foreground:getComputedStyle(n).color,background:getComputedStyle(n.closest('.card')).backgroundColor}));const rgb=s=>s.match(/[\d.]+/g).map(Number);const ratio=contrast(rgb(category.foreground),rgb(category.background));assert(ratio>=4.5);contrasts.push({source:'actual class badge',class:c.case,...category,ratio,threshold:4.5});
  manual.push({reference_class:c.case,input:c.input,HTTP:200,response:result});await page.click('#step-tab-0');await until(()=>page.$eval('#step-0',n=>!n.hidden));console.log('AZURE_MANUAL_CLASS',c.case,'PASS');
 }
 fs.mkdirSync(path.join(output,'screenshots'),{recursive:true});
 if(!fs.existsSync(manualCheckpoint)) for(const width of [1440,390]){await page.setViewportSize({width,height:1000});await pause(75);await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'screenshots',`azure-manual-${width}.png`),fullPage:true,animations:'disabled'});}
 await page.setViewportSize({width:1440,height:1000});await until(()=>page.evaluate(()=>getComputedStyle(document.querySelector('main')).paddingLeft==='40px'));await page.click('#mode-auto');await until(()=>page.getAttribute('#mode-auto','aria-pressed').then(x=>x==='true'));phase='automatic';await page.click('#replay-start');
 for(let i=0;i<10;i++){
  await until(()=>page.$eval('#replay-counter',(n,i)=>Number(n.textContent)===i+1,i),75000);await until(()=>page.$eval('#replay-panel',n=>n.dataset.state==='waiting'),75000);
  const r=proof.observations[i];assert.equal(await page.textContent('#replay-source'),labels[r.ground_truth_class]);assert.equal(await page.textContent('#replay-prediction'),labels[r.rf_e4_predicted_class]);
  const sent=requests.filter(v=>v.phase==='automatic')[i];assert.deepEqual(sent.input,data.observations[i].measurements);automatic.push({position:i+1,source_class:r.ground_truth_class,predicted_class:r.rf_e4_predicted_class,agrees:r.ground_truth_class===r.rf_e4_predicted_class,input:sent.input});console.log('AZURE_REPLAY',i+1,'PASS');
 }
 assert(automatic.some(r=>!r.agrees));assert.equal(new Set(automatic.map(r=>r.predicted_class)).size,5);
 for(const width of [1440,390]){await page.setViewportSize({width,height:1000});await pause(75);await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'screenshots',`azure-automatic-${width}.png`),fullPage:true,animations:'disabled'});}
 await page.click('#replay-pause');const stopped=requests.length;await pause(5500);assert.equal(requests.length,stopped);
 phase='restart';await page.click('#replay-restart');await until(()=>page.$eval('#replay-panel',n=>n.dataset.state==='waiting'),75000);assert.equal(await page.textContent('#replay-counter'),'1');assert.deepEqual(requests.at(-1).input,data.observations[0].measurements);
 await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));});assert.equal(await page.getAttribute('#replay-panel','data-state'),'paused');const hidden=requests.length;await pause(5500);assert.equal(requests.length,hidden);
 await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:false});document.dispatchEvent(new Event('visibilitychange'));});await page.click('#mode-manual');phase='manual_outside';
 const outside={vdc1:1000,vdc2:500,idc1:20,idc2:10};for(const[k,v]of Object.entries(outside))await page.fill('#'+k,String(v));let pending=page.waitForResponse(r=>r.url()===api+'/api/predict'&&r.request().method()==='POST');await page.click('#predict-button');const response=await pending;const outsideResult=await response.json();assert.equal(response.status(),200);assert(outsideResult.warnings.length>0);await until(()=>page.$eval('#result-content',n=>!n.hidden));assert.equal(await page.$eval('#result-warnings',n=>n.hidden),false);
 // Inspect actual computed text/background pairs that axe marked inconclusive on bars.
 await page.click('#step-tab-2');await until(()=>page.$eval('#step-2',n=>!n.hidden));
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});await pause(75);
  for(const tab of ['voltage-tab','current-tab']){await page.click('#'+tab);for(const id of ['bar-value1','bar-value2']){
   const colors=await page.$eval('#'+id,n=>{const c=getComputedStyle(n);return{foreground:c.color,background:c.backgroundColor,font_px:parseFloat(c.fontSize),font_weight:c.fontWeight,text:n.textContent};});
   const rgb=s=>s.match(/[\d.]+/g).map(Number);const ratio=contrast(rgb(colors.foreground),rgb(colors.background));assert(ratio>=4.5);contrasts.push({width,chart:tab,element:id,...colors,ratio,threshold:4.5});
  }}
  assert((await page.evaluate(()=>document.documentElement.scrollWidth))<=width);
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'screenshots',`azure-chart-${width}.png`),fullPage:true,animations:'disabled'});
 }
 await page.click('#step-tab-0');await until(()=>page.$eval('#step-0',n=>!n.hidden));await page.click('#mode-auto');
 // Controlled failure only: abort Azure in browser; never return a fabricated success.
 await page.route(api+'/**',route=>route.abort('failed'));await page.clock.install();await page.click('#replay-start');await page.clock.fastForward(121000);await until(()=>page.$eval('#replay-panel',n=>n.dataset.state==='error'));
 assert.equal(await page.textContent('#replay-prediction'),'Not evaluated');assert.equal(await page.$eval('#result-content',n=>n.hidden),true);
 const autoRequests=requests.filter(r=>r.phase==='automatic');const gaps=autoRequests.slice(1).map((r,i)=>r.start_ms-autoRequests[i].finish_ms);assert(gaps.every(ms=>ms>=4800));assert.equal(maxActive,1);assert(requests.length<=18);assert.deepEqual(errors,[]);
 const report={status:'PASS',browser_origin:base,API:api,health,manual_reference_cases:manual,automatic_observations:automatic,real_prediction_requests:requests.filter(r=>r.finish_ms).map(({request,...r})=>r),sequential:{maximum_active:maxActive,response_end_to_next_request_ms:gaps,timer_ms:5000,measurement_tolerance_ms:200},pause_no_future_requests:true,restart_first_observation:true,simulated_hidden_tab_pauses:true,manual_outside_response:outsideResult,controlled_failure:{method:'Browser abort and virtual-time startup expiry; no fabricated response',no_prediction:true},manual_contrast_review:{method:'Computed foreground and opaque background, WCAG relative luminance; visually inspect screenshots; disabled controls excluded. No text-shadow credit.',former_white_over_unfilled_ratio:contrast([255,255,255],[238,245,248]),former_dark_over_teal_ratio:contrast([16,43,63],[8,126,153]),final_bar_checks:contrasts,limitations:'Sampled rendered states, not exhaustive assistive-technology certification.'},source:'Actual existing Azure model requests from an already-approved localhost origin; no mocked successful response. Historical fixtures are parity checks, not independent accuracy.',screenshots:['azure-manual-1440.png','azure-manual-390.png','azure-automatic-1440.png','azure-automatic-390.png']};
 fs.writeFileSync(path.join(output,'Azure_Integration.json'),JSON.stringify(report,null,2)+'\n');console.log('AZURE_INTEGRATION_PASS',report.real_prediction_requests.length);
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1)});
