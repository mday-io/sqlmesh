import subprocess, sys, os, json, time, importlib.metadata as md
from pathlib import Path
out=Path.cwd()/'diagnosis-output'; out.mkdir(exist_ok=True)
harness=Path(__file__).resolve().parent
mode=sys.argv[1]
env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(harness),str(Path.cwd())]);env['PYTHONFAULTHANDLER']='1';env['DIAG_GC_MODE']=mode
(out/'provenance.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'python':sys.version,'mode':mode,'deps':{n:md.version(n) for n in ['sqlglot','duckdb','pytest','pydantic']}},indent=2))
subprocess.run([sys.executable,'-c',"import sqlmesh.core.constants as c;c.MAX_FORK_WORKERS=1;from sqlmesh import Context;ctx=Context(paths='examples/sushi');print(len(ctx.models));ctx.close()"],check=True)
results=[];started=time.monotonic()
for i in range(30):
 if time.monotonic()-started>1100:break
 args=[sys.executable,'-m','pytest','-vv','-s','-p','prefork_probe']
 args+=['tests/test_forking.py'] if mode=='target-only' else ['-m','isolated and not pyspark']
 with (out/f'repeat-{i}.log').open('w') as f:
  try:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120);code=r.returncode
  except subprocess.TimeoutExpired:code=124
 result={'repeat':i,'exit_code':code};results.append(result);print(json.dumps(result),flush=True)
 (out/'results.json').write_text(json.dumps(results,indent=2))
 if code:
  for core in Path('/tmp').glob('sqlmesh-core-*'):
   with (out/f'native-{i}-{core.name}.log').open('w') as f:
    try:subprocess.run(['gdb','-batch','-ex','thread apply all bt',sys.executable,str(core)],stdout=f,stderr=subprocess.STDOUT,timeout=90)
    except subprocess.TimeoutExpired:pass
   core.unlink(missing_ok=True)
sys.exit(any(r['exit_code'] for r in results))
