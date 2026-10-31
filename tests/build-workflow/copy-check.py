#!/usr/bin/env python3
"""Actual DLL-copy Bash with SCP stand-ins; static upload-condition regression check."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile
import yaml

parser=argparse.ArgumentParser()
parser.add_argument('--workflow',type=Path,default=Path(__file__).resolve().parents[2]/'.github/workflows/auto-dll-build.yml')
args=parser.parse_args()
steps=yaml.safe_load(args.workflow.read_text())['jobs']['build-dll']['steps']
copy=next(x for x in steps if x['name']=='Copy DLL files Over To Linux')
upload=next(x for x in steps if x['name']=='Upload Compiled DLL Artifact')
assert copy['id']=='copy_dll'
assert upload['if']=="${{ always() && steps.build.outcome == 'success' && steps.copy_dll.outcome == 'success' }}"
stub=r'''#!/usr/bin/env python3
import os,sys
from pathlib import Path
target=Path(sys.argv[-1]);name=target.name;case=os.environ['CASE']
if case=='dll_failure' and name.endswith('.dll'):
 target.write_bytes(b'partial DLL transfer');sys.exit(1)
if case=='pdb_failure' and name.endswith('.pdb'):
 target.write_bytes(b'partial PDB transfer');sys.exit(1)
if (case=='empty_dll' and name.endswith('.dll')) or (case=='empty_pdb' and name.endswith('.pdb')):
 target.write_bytes(b'');sys.exit(0)
target.write_bytes(b'current transfer '+name.encode('ascii'))
'''
cases=[('release_success','Release',True),('debug_success','Debug',True),
       ('dll_failure','Release',False),('pdb_failure','Debug',False),
       ('empty_dll','Release',False),('empty_pdb','Debug',False)]
for case,configuration,success in cases:
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);bin_dir=root/'bin';bin_dir.mkdir()
        scp=bin_dir/'scp';scp.write_text(stub);scp.chmod(0o755)
        artifacts=root/'artifacts';artifacts.mkdir()
        (artifacts/'CvGameCoreDLL.dll').write_bytes(b'OLD DLL')
        (artifacts/'CvGameCoreDLL.pdb').write_bytes(b'OLD PDB')
        script=copy['run'].replace('${{ matrix.configuration }}',configuration)
        assert '${{' not in script
        r=subprocess.run(['bash','-c',script],cwd=root,capture_output=True,text=True,
                         env=dict(os.environ,PATH=str(bin_dir)+os.pathsep+os.environ['PATH'],CASE=case))
        assert (r.returncode==0)==success,(case,r.stderr)
        for p in artifacts.iterdir():assert p.read_bytes() not in [b'OLD DLL',b'OLD PDB']
        if success:
            assert (artifacts/'CvGameCoreDLL.dll').stat().st_size>0
            assert (artifacts/'CvGameCoreDLL.pdb').exists()==(configuration=='Debug')
            if configuration=='Debug':assert (artifacts/'CvGameCoreDLL.pdb').stat().st_size>0
        print(case+': expected copy outcome')
print('6 actual-block copy cases and static copy-outcome upload guard passed; no network or Actions expression engine invoked')
