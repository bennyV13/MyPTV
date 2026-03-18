# METS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a real-time, "tee-buffered" action logging system for MyPTV that captures parameters, console output, and errors into a JSONL file.

**Architecture:** 
1. Create a `logging_utils.py` module in the `myptv` package with a `Tee` stream and an `ActionLogger` context manager.
2. Integrate this context manager into the `workflow` class in `workflow.py` to wrap all automated actions.

**Tech Stack:** Python 3.x, `json`, `io`, `sys`, `datetime`, `traceback`.

---

### Task 1: Implement `myptv.logging_utils`

**Files:**
- Create: `MyPTV/myptv/logging_utils.py`
- Test: `MyPTV/tests/test_logging_utils.py` (New file)

- [ ] **Step 1: Write a test for the ActionLogger**
Create `MyPTV/tests/test_logging_utils.py` and add a test that verifies:
1. Output is printed to terminal (captured in test runner).
2. Output is saved to `myptvlog.jsonl`.
3. Success status is recorded.
4. Error and traceback are recorded on failure.

- [ ] **Step 2: Run the test and verify it fails**
Run: `./venv/bin/python -m pytest MyPTV/tests/test_logging_utils.py`
Expected: `ModuleNotFoundError: No module named 'myptv.logging_utils'`

- [ ] **Step 3: Implement `ActionLogger` and `Tee`**
Create `MyPTV/myptv/logging_utils.py` with the following:
```python
import sys
import io
import json
import traceback
from datetime import datetime

class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

class ActionLogger(object):
    def __init__(self, action, parameters, param_file, log_fname='myptvlog.jsonl'):
        self.action = action
        self.parameters = parameters
        self.param_file = param_file
        self.log_fname = log_fname
        self.buffer = io.StringIO()
        self.original_stdout = sys.stdout
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        sys.stdout = Tee(self.original_stdout, self.buffer)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        sys.stdout = self.original_stdout
        
        status = "success" if exc_type is None else "failed"
        error_msg = None
        if exc_type:
            error_msg = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))

        log_entry = {
            "timestamp": self.start_time.isoformat(),
            "action": self.action,
            "param_file": self.param_file,
            "parameters": self.parameters,
            "status": status,
            "duration_seconds": duration,
            "output": self.buffer.getvalue(),
            "error": error_msg
        }

        with open(self.log_fname, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # We don't suppress exceptions
        return False
```

- [ ] **Step 4: Run the test and verify it passes**
Run: `./venv/bin/python -m pytest MyPTV/tests/test_logging_utils.py`
Expected: PASS

- [ ] **Step 5: Commit changes**
```bash
git add MyPTV/myptv/logging_utils.py MyPTV/tests/test_logging_utils.py
git commit -m "feat: add ActionLogger and Tee utility for experimental tracking"
```

---

### Task 2: Integrate into `workflow.py`

**Files:**
- Modify: `MyPTV/example/workflow.py`
- Modify: `Data/20260315_frames/workflow.py` (and others if needed)

- [ ] **Step 1: Add parameter extraction helper to `workflow` class**
In `workflow.py`, add `get_action_params` method:
```python
    def get_action_params(self, action):
        '''
        Extracts parameters for a specific action as a dictionary.
        '''
        try:
            action_params = self.params[self.params['operation'] == action]
            return dict(zip(action_params['param'], action_params['value']))
        except:
            return {}
```

- [ ] **Step 2: Wrap action dispatch in `__init__`**
Modify `workflow.__init__`:
```python
        # perform the wanted action:
        if action is None:
            print('Started workflow with no particular action.')
            
        elif action != None:
            from myptv.logging_utils import ActionLogger
            params_to_log = self.get_action_params(action)
            
            with ActionLogger(action, params_to_log, self.param_file_path):
                # ... existing if/elif block ...
```

- [ ] **Step 3: Verify with a dry-run**
Run the workflow with the `help` action.
Run: `./venv/bin/python Data/20260315_frames/workflow.py Data/20260315_frames/params_file.yml help`
Check: `Data/20260315_frames/myptvlog.jsonl` exists and contains the "help" action log.

- [ ] **Step 4: Commit changes**
```bash
git add MyPTV/example/workflow.py Data/20260315_frames/workflow.py
git commit -m "feat: integrate ActionLogger into workflow system"
```

---

### Task 3: Final Validation and Cleanup

- [ ] **Step 1: Run full test suite**
Run all tests in the `MyPTV` directory.
- [ ] **Step 2: Final log format check**
Ensure all fields in `myptvlog.jsonl` are correctly populated.
- [ ] **Step 3: Clean up temporary files**
Remove any `myptvlog.jsonl` created during testing from the root directory.
- [ ] **Step 4: Commit and finalize**
```bash
git commit -am "chore: finalize logging system implementation"
```
