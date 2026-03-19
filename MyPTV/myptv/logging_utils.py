import sys
import io
import json
import traceback
from datetime import datetime


class Tee(object):
    """
    A file-like object that multiplexes output to multiple streams.
    """
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
    """
    Context manager that captures console output (stdout and stderr) 
    and appends a single JSON object to a log file upon exit.
    """
    def __init__(self, action, parameters, param_file, log_fname='myptvlog.jsonl', comment=""):
        import os
        self.action = action
        self.parameters = parameters
        self.param_file = param_file
        self.comment = comment
        
        # determine the log file path:
        # If param_file exists, save log in its directory.
        if os.path.exists(param_file):
            log_dir = os.path.dirname(os.path.abspath(param_file))
            self.log_fname = os.path.join(log_dir, log_fname)
        else:
            self.log_fname = log_fname
            
        self.buffer = io.StringIO()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        # Redirect both stdout and stderr to the same buffer
        tee = Tee(self.original_stdout, self.buffer)
        sys.stdout = tee
        sys.stderr = Tee(self.original_stderr, self.buffer)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
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
            "comment": self.comment,
            "output": self.buffer.getvalue(),
            "error": error_msg
        }

        with open(self.log_fname, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # We don't suppress exceptions
        return False
