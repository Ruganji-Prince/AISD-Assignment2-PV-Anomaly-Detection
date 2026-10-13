"""Optional isolated audit reproduction; never overwrites approved submission evidence."""
from pathlib import Path
import shutil,sys,subprocess,json
ROOT=Path(__file__).resolve().parents[1]
def main():
    scratch=ROOT/'.cache/phase1_audit_reproduction'
    if scratch.exists():raise FileExistsError('Choose an unused reproduction folder; preserve prior outputs.')
    folder=scratch/'phase1_strategy';folder.mkdir(parents=True)
    for name in ['download_primary.py','audit_primary.py']:
        shutil.copy2(ROOT/'phase1_strategy'/name,folder/name)
        subprocess.run([sys.executable,'-B','-X','utf8',str(folder/name)],check=True)
    original=json.loads((ROOT/'phase1_strategy/primary_audit.json').read_text())
    repeated=json.loads((folder/'primary_audit.json').read_text())
    for key in ['raw_N','raw_total_columns','raw_predictors','raw_missing_cells','raw_complete_rows','raw_incomplete_rows','class_counts','paired_zero_rows','group_rule','proposed_split','excluded_separator_rows','validation_subblocks']:
        assert original[key]==repeated[key],key
    print('Independent audit reproduced in ignored scratch folder; official evidence/PDF unchanged.')
if __name__=='__main__':main()
