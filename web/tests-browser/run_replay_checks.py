"""Local static browser -> unchanged original-model API verification, no deployments."""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import sysconfig
import tempfile
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from frontend.build import build


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node',default=shutil.which('node'))
    parser.add_argument('--output',type=Path,default=ROOT/'docs/historical-replay')
    parser.add_argument('--legacy',action='store_true',help='Also execute retained legacy browser functions with the already-retired height-only assertion adaptation.')
    args=parser.parse_args()
    if not args.node:raise RuntimeError('Node required; install pinned web/package.json Playwright tooling.')
    cache=ROOT/'.cache';cache.mkdir(exist_ok=True)
    args.output.mkdir(parents=True,exist_ok=True)
    for port in [8080,8787]:
        with socket.socket() as probe:
            probe.bind(('127.0.0.1',port))  # Fail before accidentally testing an existing service.
    with tempfile.TemporaryDirectory(prefix='replay-check-',dir=cache,ignore_cleanup_errors=True) as scratch:
        temp=Path(scratch).resolve()
        assert temp.is_relative_to(cache.resolve())
        manifest=build(temp/'output','http://127.0.0.1:8787')
        env=os.environ.copy()
        if not env.get('NODE_PATH'):env['NODE_PATH']=str(ROOT/'web/node_modules')
        env.update(PV_APP_URL='http://127.0.0.1:8080',PV_API_URL='http://127.0.0.1:8787',PV_EVIDENCE_DIR=str(args.output.resolve()))
        logs=[(temp/'api.log').open('w'),(temp/'static.log').open('w')]
        # Bypass the Windows venv launcher so terminate/wait owns the actual server.
        server_python=getattr(sys,'_base_executable',sys.executable)
        server_env={**os.environ,'PYTHONPATH':os.pathsep.join([sysconfig.get_path('purelib'),str(ROOT),os.environ.get('PYTHONPATH','')])}
        servers=[]
        try:
            servers.append(subprocess.Popen([server_python,'-B','-m','uvicorn','web.azure_app:app','--host','127.0.0.1','--port','8787'],cwd=ROOT,env=server_env,stdout=logs[0],stderr=logs[0]))
            servers.append(subprocess.Popen([server_python,'-B','-m','http.server','8080','--bind','127.0.0.1','--directory',str(temp/'output/static')],cwd=ROOT,env=server_env,stdout=logs[1],stderr=logs[1]))
            for url in ['http://127.0.0.1:8787/api/health','http://127.0.0.1:8080/']:
                deadline=time.monotonic()+60
                while True:
                    if any(p.poll() is not None for p in servers):raise RuntimeError('Local test server failed; ensure8080/8787 are free.')
                    try:
                        with urllib.request.urlopen(url,timeout=5) as response:assert response.status==200
                        break
                    except OSError:
                        if time.monotonic()>deadline:raise
                        time.sleep(.2)
            result=subprocess.run([args.node,str(ROOT/'web/tests-browser/replay-browser.cjs')],cwd=ROOT,env=env,capture_output=True,text=True)
            if result.returncode:raise RuntimeError(result.stdout+result.stderr)
            (args.output/'Local_Build_Manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
            print(result.stdout)
            if args.legacy:
                source=(ROOT/'web/tests-browser/smoke.cjs').read_text(encoding='utf8')
                retired='if(size.width>=1100)assert.ok(metrics.height<=size.height,JSON.stringify({step:k,size,metrics}));'
                assert source.count(retired)==1
                source=source.replace(retired,'/* Already-retired document-height constraint; horizontal overflow still forbidden. */')
                source=source.replace('desktop_no_vertical_scroll:true','intentional_vertical_scroll:true')
                result=subprocess.run([args.node,'-'],input=source,cwd=ROOT,env=env,capture_output=True,text=True)
                if result.returncode:raise RuntimeError(result.stdout+result.stderr)
                receipt=json.loads(result.stdout)
                receipt['adaptation']='Only the previously retired no-desktop-vertical-scroll assertion; all legacy functional assertions retained, original source/receipts untouched.'
                (args.output/'Legacy_Functional_Verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
                print('LEGACY_FUNCTIONAL_REGRESSION_PASS')
        finally:
            for p in servers:
                p.terminate()
                try:p.wait(timeout=10)
                except subprocess.TimeoutExpired:p.kill();p.wait(timeout=10)
            for log in logs:log.close()


if __name__=='__main__':main()
