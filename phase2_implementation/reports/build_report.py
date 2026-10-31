"""Rebuild only the IEEE preprocessing report from compact evidence and source."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import re

HERE=Path(__file__).resolve().parent
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler',default=shutil.which('tectonic'),help='Tectonic executable; defaults to PATH')
    args=parser.parse_args()
    if not args.compiler:parser.error('Install Tectonic or pass --compiler; no experiment runner is needed')
    subprocess.run([sys.executable,'-B',str(HERE/'generate_report_source.py')],check=True)
    with tempfile.TemporaryDirectory(prefix='pv-preprocessing-report-') as work:
        proc=subprocess.run([args.compiler,'--keep-logs','--outdir',work,'Assignment3_Phase2.tex'],cwd=HERE,capture_output=True,text=True,encoding='utf8',errors='replace')
        if proc.returncode:
            print(proc.stdout);print(proc.stderr);raise RuntimeError('IEEE PDF compilation failed')
        log=(Path(work)/'Assignment3_Phase2.log').read_text(errors='replace')
        assert 'Overfull' not in log, 'Inspect overflowing report content before publication'
        assert not re.search(r'(?:Reference|Citation).*undefined',log), 'Unresolved report reference'
        shutil.copyfile(Path(work)/'Assignment3_Phase2.pdf',HERE/'Assignment3_Phase2.pdf')
    import pymupdf
    with pymupdf.open(HERE/'Assignment3_Phase2.pdf') as doc:
        assert sum(len(p.get_images()) for p in doc)==8
        text=''.join(p.get_text() for p in doc)
        assert '??' not in text
        pages=len(doc)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    record=dict(report='Assignment3_Phase2.pdf',pages=pages,sha256=sha(HERE/'Assignment3_Phase2.pdf'),
                source_sha256=sha(HERE/'Assignment3_Phase2.tex'),class_sha256=sha(HERE/'IEEEtran.cls'),
                document_class='IEEEtran',mode='conference',diagnostic_figures=8,
                unresolved_references=0,overfull_boxes=0,
                scope='Preprocessing and feature engineering only; no downstream evaluation')
    (HERE/'Report_Verification.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
