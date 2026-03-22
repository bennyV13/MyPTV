import json
import os
import pytest
from myptv.logging_utils import ActionLogger

def test_action_logger_newline_replacement(tmp_path):
    """
    Verify ActionLogger replaces \n with '. ' in output, error, and comment.
    """
    log_file = tmp_path / "test_newline_log.jsonl"
    action = "test_action"
    parameters = {"p1": 1}
    param_file = "non_existent.yml"
    comment = "This is a\ncomment."
    
    with ActionLogger(action, parameters, param_file, log_fname=str(log_file), comment=comment) as logger:
        print("Line 1\nLine 2")
        # No exception here

    assert log_file.exists()
    with open(log_file, 'r') as f:
        log_data = json.loads(f.read().strip())
        
    assert log_data["output"] == "Line 1. Line 2. "
    assert log_data["comment"] == "This is a. comment."
    assert log_data["error"] is None

def test_action_logger_error_newline_replacement(tmp_path):
    """
    Verify ActionLogger replaces \n with '. ' in error traceback.
    """
    log_file = tmp_path / "test_error_newline_log.jsonl"
    action = "test_error"
    parameters = {}
    param_file = "non_existent.yml"
    
    try:
        with ActionLogger(action, parameters, param_file, log_fname=str(log_file)):
            raise ValueError("Error with\nnewline.")
    except ValueError:
        pass

    assert log_file.exists()
    with open(log_file, 'r') as f:
        log_data = json.loads(f.read().strip())
        
    assert "ValueError: Error with. newline." in log_data["error"]
    assert "\n" not in log_data["error"]
