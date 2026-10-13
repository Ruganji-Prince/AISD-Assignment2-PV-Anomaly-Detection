"""Retrieve the approved primary source at its recorded immutable Git commit."""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'data/raw/candidate_evidence'
COMMIT = 'e9ed8ad8072dcb3ffc643b0f3604219798708551'
EXPECTED = {
    'dataset_amb.mat':'e4619812a5b6c1331332248f052cb09938f9a43ccac8bcc512796c6e906da7e0',
    'dataset_elec.mat':'c04ed3fcc0e338703e87d387b1ce6ef51da1848e77b4d491e62afe08934ce494',
    'README.md':'5204f6da3e825f093779e8df4f19f66efb7268a2ecb3a3ae81e298caac9e01ca',
    'LICENSE':'c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4',
}

def main() -> None:
    RAW.mkdir(parents=True,exist_ok=True)
    manifest = []
    for name,expected in EXPECTED.items():
        path=RAW/f'clayton-h-costa_{name}'
        url=f'https://raw.githubusercontent.com/clayton-h-costa/pv_fault_dataset/{COMMIT}/{name}'
        if path.exists():
            data=path.read_bytes()
        else:
            req=urllib.request.Request(url,headers={'User-Agent':'AISD-Phase1-audit'})
            with urllib.request.urlopen(req,timeout=60) as response:
                data=response.read(30*1024*1024+1)
            if len(data)>30*1024*1024:
                raise ValueError(f'Download exceeds 30 MiB bound: {name}')
        actual=hashlib.sha256(data).hexdigest()
        if actual!=expected:
            raise ValueError(f'Checksum mismatch: {name}; original file will not be overwritten.')
        if not path.exists():
            with path.open('xb') as output:
                output.write(data)
        manifest.append({'name':path.name,'source_url':url,'commit':COMMIT,'bytes':len(data),'sha256':actual})
        print(f'Verified {name}: {len(data):,} bytes')
    (ROOT/'phase1_strategy/primary_source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

if __name__=='__main__':
    main()
