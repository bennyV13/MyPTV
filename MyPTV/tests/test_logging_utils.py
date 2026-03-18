import os
import json
import sys
import io
import pytest
from myptv.logging_utils import ActionLogger, Tee

def test_tee_stdout(capsys):
    """
    Verify that Tee writes to both original and buffer.
    """
    buffer = io.StringIO()
    original_stdout = sys.stdout
    tee = Tee(original_stdout, buffer)
    
    test_message = "Hello, Tee!\n"
    tee.write(test_message)
    tee.flush()
    
    captured = capsys.readouterr()
    assert test_message in captured.out
    assert buffer.getvalue() == test_message

def test_action_logger_success(tmp_path):
    """
    Verify ActionLogger captures output and saves to jsonl on success.
    """
    log_file = tmp_path / "test_log.jsonl"
    action = "test_action"
    params = {"param1": "val1"}
    param_file = "test_params.yml"
    
    with ActionLogger(action, params, param_file, log_fname=str(log_file)) as logger:
        print("This is a test message")
        print("Another message")
    
    assert log_file.exists()
    with open(log_file, 'r') as f:
        log_data = json.loads(f.read())
        
    assert log_data["action"] == action
    assert log_data["parameters"] == params
    assert log_data["param_file"] == param_file
    assert log_data["status"] == "success"
    assert "This is a test message" in log_data["output"]
    assert "Another message" in log_data["output"]
    assert log_data["error"] is None
    assert "timestamp" in log_data
    assert "duration_seconds" in log_data

def test_action_logger_failure(tmp_path):
    """
    Verify ActionLogger captures traceback and saves to jsonl on failure.
    """
    log_file = tmp_path / "test_log.jsonl"
    action = "failing_action"
    
    with pytest.raises(ValueError, match="Test error"):
        with ActionLogger(action, {}, "params.yml", log_fname=str(log_file)):
            print("Before failure")
            raise ValueError("Test error")
            
    assert log_file.exists()
    with open(log_file, 'r') as f:
        log_data = json.loads(f.read())
        
    assert log_data["action"] == action
    assert log_data["status"] == "failed"
    assert "Before failure" in log_data["output"]
    assert "ValueError: Test error" in log_data["error"]
    assert "traceback" in log_data["error"].lower()
