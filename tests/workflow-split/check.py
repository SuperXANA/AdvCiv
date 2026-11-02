from pathlib import Path
import os,re,subprocess,tempfile,sys,yaml
workflow=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'.github/workflows/auto-dll-build.yml'
doc=yaml.safe_load(workflow.read_text())
steps=doc['jobs']['build-dll']['steps']
prepare=next(s for s in steps if s['name']=='Prepare CvGameCoreDLL Sources & Hash Verification')
build=next(s for s in steps if s.get('id')=='build')
upload=next(s for s in steps if s['name']=='Upload Source Verification Diagnostics')
assert prepare.get('id')=='prepare_sources'
assert len([s for s in steps if s.get('id')=='prepare_sources'])==1
assert 'source_verification_started=true' in prepare['run']
assert 'source_verification_started=true' not in build['run']
assert 'build_started=true' in build['run']
def condition(expr,outputs):
 match=re.fullmatch(r"\$\{\{ always\(\) && steps\.([a-z_]+)\.outputs\.([a-z_]+) == 'true' \}\}",expr)
 assert match,expr
 owner,key=match.groups()
 return outputs.get(owner,{}).get(key)=='true'
negative="${{ always() && steps.build.outputs.source_verification_started == 'true' }}"
cases=0;negative_failures=0
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp)
 for cfg in ('Release','Debug'):
  for mode in ('success','hash_mismatch','sync_failure'):
   cwd=root/(cfg+'-'+mode);cwd.mkdir();(cwd/'CvGameCoreDLL').mkdir();binpath=cwd/'bin';binpath.mkdir()
   (cwd/'CvGameCoreDLL/test.cpp').write_text('int fixture_source;\n')
   (cwd/'CvGameCoreDLL/test.h').write_text('#pragma once\n')
   (binpath/'rsync').write_text('#!/bin/bash\nif [ "$FIXTURE_MODE" = sync_failure ]; then exit 7; fi\nexit 0\n')
   (binpath/'ssh').write_text('#!/bin/bash\nif [ "$FIXTURE_MODE" = hash_mismatch ]; then\n sed "s/^[0-9a-f]\\{64\\}/0000000000000000000000000000000000000000000000000000000000000000/" expected-sources.txt\nelse\n cat expected-sources.txt\nfi\n')
   for script in binpath.iterdir():script.chmod(0o755)
   output=cwd/'step-output';output.write_text('')
   env=dict(os.environ,PATH=str(binpath)+os.pathsep+os.environ['PATH'],GITHUB_OUTPUT=str(output),FIXTURE_MODE=mode)
   env.update({k:str(v) for k,v in prepare['env'].items()})
   command=prepare['run'].replace('${{ matrix.configuration }}',cfg).replace('${{ github.sha }}','1'*40)
   result=subprocess.run(['bash','-c',command],cwd=cwd,env=env,capture_output=True,text=True)
   assert (result.returncode==0)==(mode=='success'),result.stderr
   values=dict(line.split('=',1) for line in output.read_text().splitlines())
   outputs={prepare['id']:values}
   expected=mode!='sync_failure'
   assert condition(upload['if'],outputs)==expected
   if expected:
    assert (cwd/'source-verification.txt').exists()
    assert (cwd/'expected-sources.txt').stat().st_size>0
    assert not condition(negative,outputs)
    negative_failures+=1
   if mode=='success':
    assert (cwd/'expected-sources.txt').read_bytes()==(cwd/'actual-sources.txt').read_bytes()
    assert 'status=passed' in (cwd/'source-verification.txt').read_text()
    assert 'configuration='+cfg in (cwd/'build-provenance.txt').read_text()
   if mode=='hash_mismatch':
    assert 'status=failed' in (cwd/'source-verification.txt').read_text()
    assert (cwd/'source-hashes.diff').stat().st_size>0
   cases+=1
assert cases==6 and negative_failures==4
print('6 actual preparation-script cases passed; old output-owner guard skips 4 expected uploads')
print('rsync/SSH are local stand-ins; no remote PowerShell, compiler or artifact service executed')
