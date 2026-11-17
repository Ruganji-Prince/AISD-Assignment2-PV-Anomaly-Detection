"""Read-only live deployment checks against the original local CLI and fixtures."""
import argparse
import json
import urllib.request
import urllib.error
from src.inference.cli import ROOT,SHA256,predict

def check(base):
    base=base.rstrip('/')
    def request(path,record=None,raw=None):
        data=json.dumps(record).encode() if record is not None else raw
        req=urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json'} if data is not None else {})
        try:
            response=urllib.request.urlopen(req,timeout=90)
            return response.status,response.read(),response.headers
        except urllib.error.HTTPError as exc:return exc.code,exc.read(),exc.headers
    status,body,headers=request('/')
    assert status==200 and b'PV Anomaly Detection' in body,(status,body[:100])
    status,body,headers=request('/api/health');health=json.loads(body)
    assert status==200 and health['status']=='ready' and health['model_sha256']==SHA256,(status,health)
    assert health['python_version'] in {'3.14.7','3.14.8','3.14.10'},health
    cases=json.loads((ROOT/'deployment/example_cases.json').read_text());checks=[]
    for case in cases:
        status,body,headers=request('/api/predict',case['input']);assert status==200,(status,body)
        actual=json.loads(body);reference=predict(case['input'])
        assert all(actual[k]==v for k,v in reference.items()),(case['case'],actual,reference)
        assert actual['predicted_class']==case['case']
        category='normal' if case['case']==0 else 'environmental_condition' if case['case']==4 else 'hardware_fault'
        assert actual['fault_category']==category
        assert 'confidence' not in actual and 'probabilities' not in actual
        checks.append({'fixture':case['case'],'predicted_class':actual['predicted_class'],'CLI_parity':True})
    synthetic=[]
    for case in json.loads((ROOT/'web/synthetic_test_cases.json').read_text()):
        status,body,headers=request('/api/predict',case['input']);assert status==200,(status,body)
        actual=json.loads(body);reference=predict(case['input'])
        assert all(actual[k]==v for k,v in reference.items())
        synthetic.append({'intent':case['intent'],'prediction':actual['predicted_class'],'CLI_parity':True})
    normal=cases[0]['input']
    invalid=[{},dict(normal,f_nv=0),dict(normal,idc1=True),dict(normal,idc2=-1),dict(normal,vdc1='300')]
    for record in invalid:
        status,body,headers=request('/api/predict',record);assert status==422,(record,status)
    for raw in [b'null',b'{bad',b'{"vdc1":NaN,"vdc2":1,"idc1":1,"idc2":1}']:
        status,body,headers=request('/api/predict',raw=raw);assert status==422,status
    status,body,headers=request('/api/predict',raw=b'x'*2049);assert status==413,status
    for asset in ['/assets/app.js','/assets/style.css','/assets/favicon.svg']:
        status,body,headers=request(asset);assert status==200,asset
    return {'status':'PASS','url':base,'anonymous_public_access':True,'health':health,'original_model_CLI_parity':checks,'synthetic_CLI_parity':synthetic,'invalid_request_checks':9,'static_assets':'PASS','no_confidence_or_calibration_claims':True}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--url',required=True);args=parser.parse_args()
    print(json.dumps(check(args.url),indent=2))
if __name__=='__main__':main()
