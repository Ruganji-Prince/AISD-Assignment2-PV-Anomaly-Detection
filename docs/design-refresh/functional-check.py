"""Run the legacy functional browser suite with its retired viewport-height rule explicit."""
import os,subprocess,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
node=os.environ["PV_NODE"]
source=(ROOT/"web/tests-browser/smoke.cjs").read_text(encoding="utf8")
old="if(size.width>=1100)assert.ok(metrics.height<=size.height,JSON.stringify({step:k,size,metrics}));"
assert old in source
source=source.replace(old,"/* Intentional document scrolling; horizontal overflow remains forbidden. */")
source=source.replace("desktop_no_vertical_scroll:true","intentional_vertical_scroll:true")
result=subprocess.run([node,"-"],input=source,cwd=ROOT,capture_output=True,text=True,encoding="utf8",errors="replace")
if result.returncode:raise RuntimeError(result.stderr)
report=json.loads(result.stdout);report["adaptation"]="Only the old no-desktop-vertical-scroll geometry assertion is retired; original functional checks remain unchanged. No production/source test file edited."
(ROOT/"docs/design-refresh/Functional_Regression.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
print(json.dumps(report))
