import gc,os,collections,json
import pytest
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
 if item.nodeid.endswith('test_parallel_load'):
  objects=gc.get_objects()
  counts=collections.Counter(type(o).__module__+'.'+type(o).__name__ for o in objects if 'duckdb' in type(o).__module__.lower() or type(o).__name__ in ['Context','DuckDBEngineAdapter'])
  del objects
  print('[DEBUG-prefork] '+json.dumps(dict(counts)),flush=True)
  if os.environ.get('DIAG_GC_MODE')=='collect':print('[DEBUG-prefork] collected='+str(gc.collect()),flush=True)
 yield
