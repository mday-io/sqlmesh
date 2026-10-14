import subprocess, sys, os, json, time, importlib.metadata as md
from pathlib import Path
out=Path.cwd()/'diagnosis-output';out.mkdir(exist_ok=True)
mode=sys.argv[1];env=os.environ.copy();env['PYTHONPATH']=str(Path.cwd());env['PYTHONFAULTHANDLER']='1'
(out/'provenance.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'python':sys.version,'mode':mode,'deps':{n:md.version(n) for n in ['sqlglot','duckdb','pytest','pydantic']}},indent=2))
prime="import sqlmesh.core.constants as c;c.MAX_FORK_WORKERS=1;from sqlmesh import Context;ctx=Context(paths='examples/sushi');ctx.close();ctx=Context(paths=['examples/multi/repo_1','examples/multi/repo_2'],gateway='memory');ctx.close()"
subprocess.run([sys.executable,'-c',prime],check=True)
nodes=['tests/test_forking.py'] if mode=='whole-file' else ['tests/test_forking.py::test_parallel_load','tests/test_forking.py::test_parallel_load_multi_repo']
results=[];started=time.monotonic()
for i in range(30):
 if time.monotonic()-started>1100:break
 for j,node in enumerate(nodes):
  args=[sys.executable,'-m','pytest',node,'-vv','-s']
  with (out/f'repeat-{i}-{j}.log').open('w') as f:
   try:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=90);code=r.returncode
   except subprocess.TimeoutExpired:code=124
  result={'repeat':i,'node':node,'exit_code':code};results.append(result);print(json.dumps(result),flush=True)
  (out/'results.json').write_text(json.dumps(results,indent=2))
sys.exit(any(r['exit_code'] for r in results))
