import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

spec=importlib.util.spec_from_file_location('runner',Path(__file__).resolve().parents[1]/'workflow/run.py')
wf=importlib.util.module_from_spec(spec); spec.loader.exec_module(wf)

class ProcessControl(unittest.TestCase):
    def test_timeout_terminates_child_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            # The child would create a marker after timeout if left running.
            script=root/'spawn.py'
            script.write_text("import subprocess,sys,time\nsubprocess.Popen([sys.executable,'-c',\"import time; from pathlib import Path; time.sleep(1); Path('orphan-marker').write_text('alive')\"])\ntime.sleep(10)\n")
            with self.assertRaises(subprocess.TimeoutExpired):
                wf.logged_process([sys.executable,str(script)],root,root/'session.log',timeout=0.25)
            time.sleep(1.2)
            self.assertFalse((root/'orphan-marker').exists())
