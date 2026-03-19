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
