import json
import os
import subprocess
import pytest

def test_migration_idempotency(tmp_path):
    # Prepare the scripts directory path relative to the worktree root
    # We'll assume the test is run from the worktree root
    script_path = "scripts/migrate_log_comments.py"
    
    log_file = tmp_path / "myptvlog.jsonl"
    with open(log_file, "w") as f:
        f.write(json.dumps({"timestamp": "2026-03-18", "action": "test"}) + "\n")
    
    # Run migration first time
    subprocess.run(["/Users/user/Desktop/Research/venv/bin/python", script_path, str(log_file)], check=True)
    
    with open(log_file, "r") as f:
        entry = json.loads(f.readline())
    assert entry["comment"] == ""
    
    # Run migration second time
    subprocess.run(["/Users/user/Desktop/Research/venv/bin/python", script_path, str(log_file)], check=True)
    
    with open(log_file, "r") as f:
        entry = json.loads(f.readline())
    assert entry["comment"] == ""
    # Ensure no duplicate keys or corruption
    assert len(entry) == 3 

def test_migration_malformed_json(tmp_path):
    script_path = "scripts/migrate_log_comments.py"
    
    log_file = tmp_path / "myptvlog.jsonl"
    with open(log_file, "w") as f:
        f.write('{"timestamp": "2026-03-18", "action": "good"}\n')
        f.write('{"malformed": json}\n')
        f.write('{"timestamp": "2026-03-18", "action": "good2"}\n')
    
    subprocess.run(["/Users/user/Desktop/Research/venv/bin/python", script_path, str(log_file)], check=True)
    
    with open(log_file, "r") as f:
        lines = f.readlines()
    
    assert len(lines) == 3
    assert json.loads(lines[0])["comment"] == ""
    assert "malformed" in lines[1]
    assert json.loads(lines[2])["comment"] == ""
