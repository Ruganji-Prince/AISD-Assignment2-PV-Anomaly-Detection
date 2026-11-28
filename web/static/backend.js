// Readiness only: reuse the existing bounded, SHA-validated health transport.
import {ensureReady,subscribeService} from './api.js';
const status=document.getElementById('backend-status');
const label=document.getElementById('backend-state');
const message=document.getElementById('backend-message');
const check=document.getElementById('backend-check');
subscribeService((state,description)=>{
 const name=state==='ready'?'ready':state==='unavailable'?'unavailable':'starting';
 status.dataset.state=name;label.textContent=name.toUpperCase();message.textContent=description;
});
async function checkReadiness(){
 check.disabled=true;
 try{await ensureReady({force:true});}
 catch(error){message.textContent=error.message;}
 finally{check.disabled=false;}
}
check.addEventListener('click',checkReadiness);
checkReadiness();
