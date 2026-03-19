# Log Comment Field Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `comment` field to all log entries in `myptvlog.jsonl` and update `ActionLogger` to support it.

**Architecture:** 
1. Update the `ActionLogger` class to accept and log an optional `comment`.
2. Create a migration script `scripts/migrate_log_comments.py` to update existing logs.
3. Use a test-driven approach to verify both new and migrated logs have the field.

**Tech Stack:** Python, JSONL, Pytest

---

### Task 1: Update ActionLogger

**Files:**
- Modify: `MyPTV/myptv/logging_utils.py`
- Test: `MyPTV/tests/test_logging_comment.py`

- [ ] **Step 1: Write the failing test for ActionLogger**

```python
import json
import os
from myptv.logging_utils import ActionLogger

def test_action_logger_with_comment(tmp_path):
    log_file = tmp_path / "test_log.jsonl"
    with ActionLogger("test_action", {"param": 1}, "non_existent.yml", log_fname=str(log_file), comment="Test comment"):
        print("Running action")
    
    with open(log_file, "r") as f:
        log_entry = json.loads(f.readline())
    
    assert "comment" in log_entry
    assert log_entry["comment"] == "Test comment"

def test_action_logger_default_comment(tmp_path):
    log_file = tmp_path / "test_log.jsonl"
    with ActionLogger("test_action", {"param": 1}, "non_existent.yml", log_fname=str(log_file)):
        print("Running action")
    
    with open(log_file, "r") as f:
        log_entry = json.loads(f.readline())
    
    assert "comment" in log_entry
    assert log_entry["comment"] == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `/Users/user/Desktop/Research/venv/bin/pytest MyPTV/tests/test_logging_comment.py -v`
Expected: FAIL with `TypeError: __init__() got an unexpected keyword argument 'comment'`

- [ ] **Step 3: Update ActionLogger implementation**

Modify `MyPTV/myptv/logging_utils.py`:
- Update `__init__` to accept `comment=""`.
- Update `__exit__` to include `"comment": self.comment` in `log_entry` dictionary, placing it after `status` and `duration_seconds`.

- [ ] **Step 4: Run test to verify it passes**

Run: `/Users/user/Desktop/Research/venv/bin/pytest MyPTV/tests/test_logging_comment.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add MyPTV/myptv/logging_utils.py MyPTV/tests/test_logging_comment.py
git commit -m "feat: add comment field to ActionLogger"
```

### Task 2: Create Migration Script

**Files:**
- Create: `scripts/migrate_log_comments.py`
- Test: `MyPTV/tests/test_migration_script.py`

- [ ] **Step 1: Write the failing test for migration**

```python
import json
import os
import subprocess
import pytest

def test_migration_idempotency(tmp_path):
    log_file = tmp_path / "myptvlog.jsonl"
    with open(log_file, "w") as f:
        f.write(json.dumps({"timestamp": "2026-03-18", "action": "test"}) + "\n")
    
    # Run migration first time
    subprocess.run(["/Users/user/Desktop/Research/venv/bin/python", "scripts/migrate_log_comments.py", str(log_file)], check=True)
    
    with open(log_file, "r") as f:
        entry = json.loads(f.readline())
    assert entry["comment"] == ""
    
    # Run migration second time
    subprocess.run(["/Users/user/Desktop/Research/venv/bin/python", "scripts/migrate_log_comments.py", str(log_file)], check=True)
    
    with open(log_file, "r") as f:
        entry = json.loads(f.readline())
    assert entry["comment"] == ""
    # Ensure no duplicate keys or corruption
    assert len(entry) == 3 

def test_migration_malformed_json(tmp_path):
    log_file = tmp_path / "myptvlog.jsonl"
    with open(log_file, "w") as f:
        f.write('{"timestamp": "2026-03-18", "action": "good"}\n')
        f.write('{"malformed": json}\n')
        f.write('{"timestamp": "2026-03-18", "action": "good2"}\n')
    
    subprocess.run(["/Users/user/Desktop/Research/venv/bin/python", "scripts/migrate_log_comments.py", str(log_file)], check=True)
    
    with open(log_file, "r") as f:
        lines = f.readlines()
    
    assert len(lines) == 3
    assert json.loads(lines[0])["comment"] == ""
    assert "malformed" in lines[1]
    assert json.loads(lines[2])["comment"] == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run: `/Users/user/Desktop/Research/venv/bin/pytest MyPTV/tests/test_migration_script.py -v`
Expected: FAIL (script doesn't exist)

- [ ] **Step 3: Implement migration script**

Create `scripts/migrate_log_comments.py` with backup logic and error handling.

- [ ] **Step 4: Run test to verify it passes**

Run: `/Users/user/Desktop/Research/venv/bin/pytest MyPTV/tests/test_migration_script.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add scripts/migrate_log_comments.py MyPTV/tests/test_migration_script.py
git commit -m "feat: add migration script for log comments"
```

### Task 3: Execute Migration on Data Log

**Files:**
- Modify: `Data/20260315_frames/myptvlog.jsonl`

- [ ] **Step 1: Run migration on actual log**

Run: `/Users/user/Desktop/Research/venv/bin/python scripts/migrate_log_comments.py Data/20260315_frames/myptvlog.jsonl`

- [ ] **Step 2: Verify migration results**

Run: `head -n 5 Data/20260315_frames/myptvlog.jsonl`
Check if `comment` field is present.

- [ ] **Step 3: Verify with workflow.py**

Run a sample action through the workflow script (assuming it uses ActionLogger):
Run: `cd Data/20260315_frames && ../../venv/bin/python workflow.py help --comment "Verifying integration"`
Check: `tail -n 1 Data/20260315_frames/myptvlog.jsonl`
Expected: Entry with `action: help` and `comment: "Verifying integration"`.

- [ ] **Step 4: Commit log changes**

```bash
git add Data/20260315_frames/myptvlog.jsonl
git commit -m "data: migrate log file to include comment field"
```
