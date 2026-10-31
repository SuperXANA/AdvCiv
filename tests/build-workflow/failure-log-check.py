#!/usr/bin/env python3
"""Exercise the actual log-copy Bash block with local SSH/SCP stand-ins."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile
import yaml

parser=argparse.ArgumentParser()
parser.add_argument('--workflow',type=Path,default=Path(__file__).resolve().parents[2]/'.github/workflows/auto-dll-build.yml')
args=parser.parse_args()
workflow=yaml.safe_load(args.workflow.read_text())
steps=workflow['jobs']['build-dll']['steps']
copy=next(s for s in steps if s['name']=='Copy Build Log files Over To Linux')
upload=next(s for s in steps if s['name']=='Upload Build Artifacts Always on Failure')
assert 'always()' in copy['if'] and "steps.build.outputs.build_started == 'true'" in copy['if']
assert 'always()' in upload['if'] and "steps.build.outcome == 'failure'" in upload['if']
assert "steps.build.outputs.build_started == 'true'" in upload['if']
script=copy['run']
for expression,value in [('${{ matrix.configuration }}','Release'),('${{ github.run_id }}','123'),
                         ('${{ github.run_attempt }}','2'),('${{ github.sha }}','abcdef')]:
    script=script.replace(expression,value)
assert '${{' not in script
stub=r'''#!/usr/bin/env python3
import os,sys
from pathlib import Path
if Path(sys.argv[0]).name=='ssh':
 print(os.environ['FAKE_TOKEN']);sys.exit(0)
name=sys.argv[-2].rsplit('/',1)[-1]
with open(os.environ['TRACE'],'a') as out:out.write(name+'\n')
case=os.environ['FAKE_CASE']
if (case=='missing_build' and name=='Build.log') or (case=='missing_optional' and name=='JustWarnings.log') or (case=='missing_timing' and name=='BuildTiming.log'):sys.exit(1)
(Path(sys.argv[-1])/name).write_text('current test log\n')
'''
for case in ['current','stale_token','missing_build','missing_optional','missing_timing']:
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);bin_dir=root/'bin';bin_dir.mkdir()
        for name in ['ssh','scp']:
            p=bin_dir/name;p.write_text(stub);p.chmod(0o755)
        artifacts=root/'artifacts';artifacts.mkdir();(artifacts/'Old.log').write_text('stale')
        trace=root/'trace'
        env=dict(os.environ,PATH=str(bin_dir)+os.pathsep+os.environ['PATH'],TRACE=str(trace),FAKE_CASE=case,
                 FAKE_TOKEN='old-run' if case=='stale_token' else '123-2-Release-abcdef')
        result=subprocess.run(['bash','-c',script],cwd=root,env=env,capture_output=True,text=True)
        assert (result.returncode==0)==(case in ['current','missing_optional','missing_timing']),(case,result.stderr)
        assert not (artifacts/'Old.log').exists()
        calls=trace.read_text().splitlines() if trace.exists() else []
        assert len(calls)==(0 if case=='stale_token' else 4),(case,calls)
        assert (artifacts/'Build.log').exists()==(case in ['current','missing_optional','missing_timing'])
        print(case+': expected log-copy result')
print('5 actual-block log collection cases passed; no network or Actions expression engine invoked')
