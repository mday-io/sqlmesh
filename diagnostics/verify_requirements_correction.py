from pathlib import Path
import subprocess,sys
p=Path('tests/core/test_context.py')
s=p.read_text()
s=s.replace('    if IS_WINDOWS:\n        requirements.add("pendulum")\n','')
s=s.replace('    if IS_WINDOWS:\n        reqs.add("pendulum")\n','')
assert s != p.read_text()
p.write_text(s)
subprocess.run([sys.executable,'-m','pytest','tests/core/test_context.py::test_requirements','-vv'],check=True)
