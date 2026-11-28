// Local static build -> mocked transport, then real unchanged local Azure-compatible API.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const root=path.resolve(__dirname,'../..'),base=process.env.PV_APP_URL||'http://127.0.0.1:8080',api=process.env.PV_API_URL||'http://127.0.0.1:8787';
const output=process.env.PV_EVIDENCE_DIR;if(!output)throw new Error('Fresh PV_EVIDENCE_DIR required.');
const data=JSON.parse(fs.readFileSync(path.join(root,'web/data/pv_historical_replay.json')));
const proof=JSON.parse(fs.readFileSync(path.join(root,'technical_evaluation/PV_Replay_Verification.json')));
const cases=JSON.parse(fs.readFileSync(path.join(root,'deployment/example_cases.json')));
const keys=['vdc1','vdc2','idc1','idc2'],sha=proof.model_sha256;
const labels=['Normal','Short Circuit','Resistive Degradation','Open Circuit','Natural Building Shade'];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn){for(let i=0;i<300;i++){if(await fn())return;await sleep(10);}throw new Error('Browser condition timed out.');}
async function state(page,s){await until(()=>page.$eval('#replay-panel',(n,s)=>n.dataset.state===s,s));}
async function go(page,k){await page.click('#step-tab-'+k);await until(()=>page.$eval('#step-'+k,n=>!n.hidden));assert.equal(await page.locator('.step-panel:visible').count(),1);}
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-proxy-server']});
 try{
  const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});const page=await context.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));let predictionCalls=[],allCalls=[],held=null,holdNext=false,failNext=false,active=0,maximumActive=0;
  await page.route(api+'/**',async route=>{
   const request=route.request(),url=request.url();allCalls.push(url);
   const headers={'access-control-allow-origin':base,'access-control-allow-methods':'GET,POST,OPTIONS','access-control-allow-headers':'content-type'};
   const send=(body,status=200)=>route.fulfill({status,headers,contentType:'application/json',body:JSON.stringify(body)});
   if(request.method()==='OPTIONS')return send({});
   if(url.endsWith('/health'))return send({status:'ready',model_sha256:sha});
   if(url.endsWith('/examples'))return send(cases.map(c=>({id:c.case,measurements:c.input,name:c.output.label})));
   if(url.endsWith('/predict')){
    const values=request.postDataJSON();assert.deepEqual(Object.keys(values),keys);predictionCalls.push(values);active++;maximumActive=Math.max(maximumActive,active);
    const result={predicted_class:4,model_sha256:sha,fault_category:'environmental',warnings:values.vdc1>364?['Outside observed TRAIN range: vdc1.']:[]};
    const finish=async()=>{try{if(failNext){failNext=false;await send({detail:'Controlled API failure'},503);}else await send(result);}catch{}finally{active--;}};
    if(holdNext){holdNext=false;held=finish;}else await finish();
   }
  });
  await page.clock.install({time:new Date('2026-11-28T10:00:00Z')});await page.clock.pauseAt(new Date('2026-11-28T10:00:00Z'));
  await page.goto(base,{waitUntil:'domcontentloaded'});await until(()=>page.$eval('#service-status',n=>n.dataset.state==='ready'));
  assert.equal(await page.getAttribute('#mode-manual','aria-pressed'),'true');assert.equal(await page.locator('#replay-panel').isVisible(),false);
  await page.clock.fastForward(20000);assert.equal(predictionCalls.length,0);
  await page.click('#mode-auto');await page.clock.fastForward(20000);assert.equal(predictionCalls.length,0);
  // UI receives an intentionally different model class, never a source-label shortcut.
  await page.click('#replay-start');await state(page,'waiting');assert.equal(predictionCalls.length,1);
  assert.deepEqual(predictionCalls[0],data.observations[0].measurements);
  assert.equal(await page.textContent('#replay-source'),labels[data.observations[0].source_class]);
  assert.equal(await page.textContent('#replay-prediction'),labels[4]);assert.match(await page.textContent('#replay-agreement'),/Disagrees/);
  assert.equal(await page.textContent('#category-badge'),'Environmental effect');assert.match(await page.textContent('#replay-interpretation'),/shade/i);
  assert.equal(await page.textContent('#diagram-source'),'MODEL PREDICTION');assert.match(await page.textContent('#diagram-caption'),/model output/);
  for(let i=1;i<25;i++){await page.clock.fastForward(5000);await until(()=>page.$eval('#replay-counter',(n,i)=>Number(n.textContent)===i+1,i));await state(page,i===24?'completed':'waiting');}
  assert.deepEqual(predictionCalls,data.observations.slice(0,25).map(r=>r.measurements));assert.equal(maximumActive,1);
  let count=allCalls.length;await page.clock.fastForward(180000);await sleep(30);assert.equal(allCalls.length,count);assert.equal(predictionCalls.length,25);
  // Pausing a waiting scheduler prevents subsequent requests.
  await page.click('#replay-restart');await state(page,'waiting');assert.equal(await page.textContent('#replay-counter'),'1');assert.deepEqual(predictionCalls.at(-1),data.observations[0].measurements);
  await page.click('#replay-pause');count=allCalls.length;await page.clock.fastForward(60000);assert.equal(allCalls.length,count);
  // A held inference must finish before the five-second scheduling delay begins.
  holdNext=true;await page.click('#replay-start');await until(()=>held!==null);let n=predictionCalls.length;await page.clock.fastForward(10000);assert.equal(predictionCalls.length,n);
  let release=held;held=null;await release();await state(page,'waiting');await page.clock.fastForward(4999);assert.equal(predictionCalls.length,n);await page.clock.fastForward(1);await state(page,'waiting');assert.equal(predictionCalls.length,n+1);
  // Switching mode invalidates a late response and clears prior prediction displays.
  await page.click('#replay-pause');holdNext=true;await page.click('#replay-start');await until(()=>held!==null);await page.click('#mode-manual');release=held;held=null;await release();await sleep(50);
  assert.equal(await page.$eval('#result-content',x=>x.hidden),true);count=allCalls.length;await page.clock.fastForward(60000);assert.equal(allCalls.length,count);
  // Visibility events are browser-simulated; no backend setting or real tab is changed.
  await page.click('#mode-auto');await page.click('#replay-start');await state(page,'waiting');
  await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));});
  await state(page,'paused');count=allCalls.length;await page.clock.fastForward(60000);assert.equal(allCalls.length,count);
  await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:false});document.dispatchEvent(new Event('visibilitychange'));});await page.clock.fastForward(10000);assert.equal(allCalls.length,count);
  // Error stops scheduling, no fabricated response or previous result remains.
  failNext=true;await page.click('#replay-start');await state(page,'error');assert.equal(await page.$eval('#result-content',n=>n.hidden),true);assert.equal(await page.textContent('#replay-prediction'),'Not evaluated');
  count=allCalls.length;await page.clock.fastForward(60000);assert.equal(allCalls.length,count);
  await page.click('#mode-manual');await page.click('#load-recorded');await until(()=>page.$eval('#recorded-select',n=>!n.disabled));
  assert.equal(await page.locator('#recorded-select optgroup').count(),5);assert.equal(await page.locator('#recorded-select option').count(),151);
  for(const group of await page.locator('#recorded-select optgroup').all())assert.equal(await group.locator('option').count(),30);
  n=predictionCalls.length;await page.selectOption('#recorded-select','2');assert.equal(predictionCalls.length,n);for(const k of keys)assert.equal(Number(await page.inputValue('#'+k)),data.observations[2].measurements[k]);
  await page.click('#reset-button');assert.equal(await page.inputValue('#recorded-select'),'');for(const k of keys)assert.equal(await page.inputValue('#'+k),'');assert.equal(predictionCalls.length,n);
  // Arbitrary valid manual input stays unrestricted and range warnings survive.
  const arbitrary={vdc1:1000,vdc2:500,idc1:20,idc2:10};for(const [k,v] of Object.entries(arbitrary))await page.fill('#'+k,String(v));
  await page.click('#predict-button');await until(()=>page.$eval('#result-content',n=>!n.hidden));assert.deepEqual(predictionCalls.at(-1),arbitrary);assert.equal(await page.$eval('#result-warnings',n=>n.hidden),false);
  await go(page,2);assert.match(await page.textContent('#bar-value1'),/1000/);await page.click('#current-tab');assert.match(await page.textContent('#bar-value1'),/20.000/);await go(page,3);assert.equal(await page.textContent('#predicted-label'),labels[4]);
  await page.focus('#step-tab-0');await page.keyboard.press('ArrowRight');await until(()=>page.$eval('#step-1',n=>!n.hidden));
  for(const width of [320,390,768,1440]){await page.setViewportSize({width,height:1000});for(let k=0;k<4;k++){await go(page,k);assert((await page.evaluate(()=>document.documentElement.scrollWidth))<=width);}}
  await go(page,0);await page.click('#observed-ranges summary');assert.equal(await page.locator('#observed-ranges tbody tr').count(),5);assert.equal(await page.locator('#observed-ranges td').count(),20);
  assert((await page.evaluate(()=>document.documentElement.scrollWidth))<=1440);
  for(const width of [320,390]){await page.setViewportSize({width,height:1000});await page.clock.runFor(100);await until(()=>page.evaluate(()=>getComputedStyle(document.querySelector('main')).paddingLeft==='12px'));const geometry=await page.evaluate(()=>({document:document.documentElement.scrollWidth,offenders:[...document.querySelectorAll('body *')].filter(n=>n.getBoundingClientRect().right>innerWidth+1).slice(0,15).map(n=>({tag:n.tagName,id:n.id,cls:n.className,width:n.getBoundingClientRect().width,right:n.getBoundingClientRect().right}))}));assert(geometry.document<=width,JSON.stringify({width,...geometry}));}
  // Retained five legacy dataset examples still populate/submit correctly through mocked transport.
  await go(page,1);await page.click('#dataset-tab');await page.selectOption('#example-select','3');for(const k of keys)assert.equal(Number(await page.inputValue('#'+k)),cases[3].input[k]);
  assert.deepEqual(errors,[]);await context.close();

  // No API routes are mocked in this context: actual HTTP original-model integration.
  const real=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});const live=await real.newPage();const realErrors=[],requests=[],responses=[];
  live.on('pageerror',e=>realErrors.push(e.message));live.on('request',r=>{if(r.url().endsWith('/api/predict'))requests.push(r.postDataJSON());});
  await live.clock.install({time:new Date('2026-11-28T11:00:00Z')});await live.clock.pauseAt(new Date('2026-11-28T11:00:00Z'));
  await live.goto(base,{waitUntil:'domcontentloaded'});await until(()=>live.$eval('#service-status',n=>n.dataset.state==='ready'));
  await live.click('#mode-auto');await live.click('#replay-start');await state(live,'waiting');
  async function verifyReal(i){const record=proof.observations[i];assert.deepEqual(requests[i],data.observations[i].measurements);assert.equal(await live.textContent('#replay-source'),labels[record.ground_truth_class]);assert.equal(await live.textContent('#replay-prediction'),labels[record.rf_e4_predicted_class]);assert.equal(await live.textContent('#predicted-label'),labels[record.rf_e4_predicted_class]);responses.push({position:i+1,source_class:record.ground_truth_class,predicted_class:record.rf_e4_predicted_class});}
  await verifyReal(0);
  for(let i=1;i<25;i++){await live.clock.fastForward(5000);await until(()=>live.$eval('#replay-counter',(n,i)=>Number(n.textContent)===i+1,i));await state(live,i===24?'completed':'waiting');await verifyReal(i);}
  assert.equal(requests.length,25);assert.equal(new Set(responses.map(r=>r.predicted_class)).size,5);assert(responses.some(r=>r.source_class!==r.predicted_class));
  await live.clock.resume(); // Replay is complete; allow accessibility tooling's own timers.
  fs.mkdirSync(path.join(output,'screenshots'),{recursive:true});
  const accessibility=[];
  async function capture(mode,width){
   await live.setViewportSize({width,height:1000});await live.evaluate(()=>window.scrollTo(0,0));
   if(process.env.PV_AXE_PATH){
    if(!await live.evaluate(()=>Boolean(window.axe)))await live.addScriptTag({path:process.env.PV_AXE_PATH});
    const audit=await live.evaluate(async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)})),incomplete:r.incomplete.map(v=>v.id)};});
    assert.deepEqual(audit.violations,[]);accessibility.push({mode,width,...audit});
   }
   await live.screenshot({path:path.join(output,'screenshots',`${mode}-${width}.png`),fullPage:true,animations:'disabled'});
  }
  // Capture completed replay with its real received prediction, without another cycle.
  for(const width of [1440,390])await capture('automatic',width);
  await live.click('#mode-manual');for(const [k,v] of Object.entries(arbitrary))await live.fill('#'+k,String(v));
  const response=live.waitForResponse(r=>r.url()===api+'/api/predict'&&r.request().method()==='POST');await live.click('#predict-button');const result=await(await response).json();await until(()=>live.$eval('#result-content',n=>!n.hidden));assert.equal(await live.textContent('#predicted-label'),labels[result.predicted_class]);assert((result.warnings||[]).length>0);assert.equal(result.model_sha256,sha);
  for(const width of [1440,390])await capture('manual',width);
  assert.deepEqual(realErrors,[]);await real.close();
  const report={status:'PASS',mocked_transport:{default_manual:true,no_start_without_action:true,all25_exact_payloads:true,maximum_inflight_requests:maximumActive,bounded25:true,no_post_completion_keepalive:true,late_response_invalidated:true,pause_stops_traffic:true,restart_resets_to_first:true,mode_switch_cancels:true,visibility_pause_no_auto_resume:true,error_stops_without_prediction:true,source_separate_from_returned_class:true,all150_manual_examples:true,arbitrary_manual_values:true,range_warnings:true,charts_and_actual_explanations:true,four_step_keyboard_navigation:true,viewports:[320,390,768,1440],range_table:true,legacy_dataset_controls:true},real_local_HTTP:{backend:'Unchanged web.azure_app:app and original RF E4; no mocked routes',source:'Local static build on8080 -> original FastAPI on8787',five_predicted_classes:true,model_sha256:sha,observations:responses,manual_out_of_range_response:result},screenshots:['automatic-1440.png','automatic-390.png','manual-1440.png','manual-390.png'],limitations:['Scheduling tests use virtual time; no five-second acquisition cadence claim.','Visibility is a simulated browser property/event.','Local real API integration does not establish live Azure availability or independent accuracy.','No deployment or production change.']};
  report.accessibility=accessibility.length?accessibility:'Not executed: supply PV_AXE_PATH for optional installed axe tooling.';
  fs.writeFileSync(path.join(output,'Browser_Verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({status:'PASS',mocked_checks:Object.keys(report.mocked_transport).length,real_HTTP_predictions:26,five_predicted_classes:true,screenshots:4,axe_views:accessibility.length}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
