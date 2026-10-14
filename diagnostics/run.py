import subprocess,sys,os,json,platform,importlib.metadata as md
from pathlib import Path
out=Path.cwd()/'diagnosis-output';out.mkdir(exist_ok=True)
harness=Path(__file__).resolve().parent
env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join([str(harness),str(Path.cwd())]);env['DIAG_OUTPUT']=str(out);env['PYTHONFAULTHANDLER']='1'
provenance={'revision_label':sys.argv[1],'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'dependencies':{n:md.version(n) for n in ['sqlmesh','sqlglot','pydantic','pendulum','pytest','numpy','pandas','pyarrow']}}
(out/'provenance.json').write_text(json.dumps(provenance,indent=2));print(json.dumps(provenance),flush=True)
commands=[('requirements',[sys.executable,'-m','pytest','tests/core/test_context.py::test_requirements','-vv','-s','-p','requirements_probe','--requirements-probe-json',str(out/'requirements-probe.jsonl')])] if os.name=='nt' else [('isolated',[sys.executable,'-m','pytest','-m','isolated and not pyspark','-v','-s']),('parallel-fresh',[sys.executable,'-m','pytest','tests/test_forking.py','-vv','-s'])]
results=[]
for label,args in commands:
 with (out/(label+'.log')).open('w') as f:
  r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=360)
 results.append({'command':args,'label':label,'exit_code':r.returncode});print(json.dumps(results[-1]),flush=True)
(out/'results.json').write_text(json.dumps(results,indent=2))
sys.exit(any(r['exit_code'] for r in results))
