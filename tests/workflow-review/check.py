from pathlib import Path
import subprocess,yaml
root=Path(__file__).resolve().parents[2]
s=(root/'.github/workflows/auto-dll-build.yml').read_text()
w=yaml.load(s,Loader=yaml.BaseLoader);job=w['jobs']['build-dll']
assert job['strategy']['matrix']['configuration']==['Release','Debug']
ps=next(x['env']['PS_CODE'] for x in job['steps'] if x.get('id')=='build')
assert ps.count('cmd.exe /c $buildCmd')==1
sync=next(x['run'] for x in job['steps'] if x.get('id')=='build')
assert sync.count('rsync ')==2 and './ Administrator@' not in sync
name=next(x['with']['name'] for x in job['steps'] if 'upload-artifact' in x.get('uses',''))
assert '${{ matrix.configuration }}' in name
assert '<add ' not in s and 'project/$CONFIG/*.log' not in s
for step in job['steps']:
 if step.get('shell')=='bash':subprocess.run(['bash','-n'],input=step['run'],text=True,check=True)
print('PASS: static workflow checks and Bash syntax; no PowerShell, SSH, runner, compiler or DLL execution')
