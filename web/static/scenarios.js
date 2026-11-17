// Illustrative operating-pattern presets, not circuit-validated fault simulations.
// No model output is consulted when generating measurements.
export const scenarioNames = ['Normal Operation','Short Circuit','Resistive Degradation','Open Circuit','Building Shade'];
export const presets = [
 {vdc1:330,vdc2:332,idc1:6.5,idc2:6.4},
 {vdc1:180,vdc2:330,idc1:8.2,idc2:6.4},
 {vdc1:305,vdc2:330,idc1:4.4,idc2:6.4},
 {vdc1:340,vdc2:332,idc1:0,idc2:6.4},
 {vdc1:315,vdc2:330,idc1:2,idc2:6.4}
];
export function generateScenario(kind, seed=42) {
 if(!Number.isInteger(kind)||kind<0||kind>4||!Number.isInteger(seed))throw new Error('Invalid scenario or seed.');
 let state=seed>>>0;
 const random=()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return state/4294967296;};
 return Object.fromEntries(Object.entries(presets[kind]).map(([key,value])=>[key,Number((value*(1+(random()*2-1)*(key.startsWith('v')?.015:.04))).toFixed(4))]));
}
