// Public preview checks with normal browser security. CORS failures are not mocked away.
const {chromium}=require('playwright');const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),base=process.env.PV_PREVIEW_URL,output=process.env.PV_EVIDENCE_DIR,api='https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io';
if(!base||!output)throw new Error('PV_PREVIEW_URL and PV_EVIDENCE_DIR required');
const labels=['Normal','Short Circuit','Resistive Degradation','Open Circuit','Natural Building Shade'];const data=JSON.parse(fs.readFileSync(path.join(root,'web/data/pv_historical_replay.json')));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));async function until(fn){for(let i=0;i<300;i++){if(await fn())return;await sleep(20);}throw new Error('Preview condition timed out.');}
(async()=>{
 const b=await chromium.launch({headless:true});try{
 const page=await b.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'}),requests=[],errors=[],consoleErrors=[];
 page.on('request',r=>{if(r.url().startsWith(api))requests.push({url:r.url(),method:r.method()});});page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});
 const response=await page.goto(base,{waitUntil:'domcontentloaded',timeout:60000});assert.equal(response.status(),200);assert.equal(await page.getAttribute('#mode-manual','aria-pressed'),'true');
 // A direct browser POST must fail at CORS; no proxy, supplied origin header or disabled security.
 const cors=await page.evaluate(async({api,values})=>{try{const r=await fetch(api+'/api/predict',{method:'POST',credentials:'omit',headers:{'Content-Type':'application/json'},body:JSON.stringify(values)});return {HTTP:r.status,body:await r.text()};}catch(e){return {blocked:true,name:e.name,message:e.message};}},{api,values:data.observations[0].measurements});
 assert.equal(cors.blocked,true);assert.equal(cors.name,'TypeError');
 // Cancel initial readiness rather than sending retries for the entire startup allowance.
 await page.click('#mode-auto');await page.click('#mode-manual');
 await page.click('#load-recorded');await until(()=>page.$eval('#recorded-select',n=>!n.disabled));assert.equal(await page.locator('#recorded-select option').count(),151);
 for(const group of await page.locator('#recorded-select optgroup').all())assert.equal(await group.locator('option').count(),30);
 for(let k=0;k<5;k++){
  const index=data.observations.findIndex(r=>r.source_class===k);await page.selectOption('#recorded-select',String(index));
  for(const key of ['vdc1','vdc2','idc1','idc2'])assert.equal(Number(await page.inputValue('#'+key)),data.observations[index].measurements[key]);
  assert.equal(await page.$eval('#result-content',n=>n.hidden),true);
 }
 await page.fill('#idc1','-1');await page.click('#predict-button');assert.equal(await page.$eval('#idc1',n=>n.validity.rangeUnderflow),true);await page.fill('#idc1','0.5');
 await page.click('#observed-ranges summary');assert.equal(await page.locator('#observed-ranges td').count(),20);
 await page.focus('#step-tab-0');await page.keyboard.press('ArrowRight');await until(()=>page.$eval('#step-1',n=>!n.hidden));
 const focus=await page.evaluate(()=>{const n=document.activeElement,c=getComputedStyle(n);return {id:n.id,visible:n.matches(':focus-visible'),outline:c.outlineStyle,width:c.outlineWidth,color:c.outlineColor};});assert.equal(focus.id,'step-tab-1');assert(focus.visible&&parseFloat(focus.width)>=2);
 for(let k=0;k<4;k++){await page.click('#step-tab-'+k);await until(()=>page.$eval('#step-'+k,n=>!n.hidden));assert.equal(await page.locator('.step-panel:visible').count(),1);}
 await page.click('#step-tab-0');await until(()=>page.$eval('#step-0',n=>!n.hidden));
 fs.mkdirSync(path.join(output,'screenshots'),{recursive:true});
 async function capture(mode,width){await page.setViewportSize({width,height:1000});await until(()=>page.evaluate(width=>getComputedStyle(document.querySelector('main')).paddingLeft===(width<500?'12px':'40px'),width));assert((await page.evaluate(()=>document.documentElement.scrollWidth))<=width);await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(output,'screenshots',`preview-${mode}-${width}.png`),fullPage:true,animations:'disabled'});}
 for(const width of [1440,390])await capture('manual',width);
 await page.setViewportSize({width:1440,height:1000});await until(()=>page.evaluate(()=>getComputedStyle(document.querySelector('main')).paddingLeft==='40px'));await page.click('#mode-auto');await page.click('#replay-start');await until(()=>page.getAttribute('#replay-panel','data-state').then(x=>x==='starting'));
 await sleep(1000);await page.click('#replay-pause');assert.equal(await page.textContent('#replay-prediction'),'Not evaluated');const stopped=requests.length;await sleep(5500);assert.equal(requests.length,stopped);
 await page.click('#replay-restart');await until(()=>page.getAttribute('#replay-panel','data-state').then(x=>x==='starting'));
 await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));});assert.equal(await page.getAttribute('#replay-panel','data-state'),'paused');await page.evaluate(()=>Object.defineProperty(document,'hidden',{configurable:true,value:false}));
 const hidden=requests.length;await sleep(5500);assert.equal(requests.length,hidden);assert.equal(await page.$eval('#result-content',n=>n.hidden),true);
 for(const width of [1440,390])await capture('automatic',width);
 await page.click('#step-tab-2');await until(()=>page.$eval('#step-2',n=>!n.hidden));const colors=await page.$eval('#bar-value1',n=>({color:getComputedStyle(n).color,background:getComputedStyle(n).backgroundColor}));assert.equal(colors.background,'rgb(255, 255, 255)');assert.deepEqual(errors,[]);
 const report={status:'PARTIAL_CORS_BLOCKED',preview:base,API:api,browser_native_POST:cors,manual_mode:{default:true,all150examples:true,source_classes:5,measurements_match_frozen_fixture:true,negative_input_rejected:true,real_inference:'BLOCKED_BY_CORS'},automatic_mode:{Start_Pause_Restart_controls:true,Pause_cancels_readiness:true,simulated_hidden_tab_pauses:true,no_auto_resume_or_future_requests:true,no_fabricated_prediction:true,real_inference:'BLOCKED_BY_CORS',live_five_second_sequence:'NOT_EXECUTED_ON_PREVIEW: CORS prevents readiness. Verified separately with actual Azure from localhost.'},UI:{four_steps:true,keyboard_focus:focus,viewports:[1440,390],ranges20cells:true,chart_label_colors:colors},page_errors:errors,console_errors:consoleErrors,network:requests,source_security:'Default Chromium security; no successful responses mocked, no proxy, no origin/credential bypass.',production_recommendation:'NO-GO until exact preview origin is separately approved and full preview-to-Azure browser inference passes.'};
 fs.writeFileSync(path.join(output,'Preview_Browser_Verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({status:report.status,preview:base,UI:'PASS',real_Azure_from_preview:'BLOCKED',screenshots:4}));
 }finally{await b.close();}
})().catch(e=>{console.error(e);process.exit(1)});
