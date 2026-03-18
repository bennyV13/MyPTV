# Design Specification: MyPTV Experimental Traceability System (METS)

**Date:** 2026-03-18
**Author:** Gemini CLI
**Status:** Draft
**Topic:** Real-time action logging for MyPTV workflows

## 1. Objective
Enable transparent, reproducible experiments by automatically capturing the state (parameters), execution context (param file), and results (full console output/errors) of every MyPTV operation into a machine-readable, append-only JSONL log.

## 2. Architecture

### 2.1 Overview
The system follows an **"Execution Envelope"** pattern. Instead of a passive logger, a context manager "wraps" the execution of MyPTV actions. This allows it to capture state before start, intercept output during execution, and handle success/failure states at completion.

### 2.2 Core Components

#### A. `myptv.logging_utils.ActionLogger` (New Module)
A Python context manager responsible for:
- **Tee Redirection:** Temporarily replaces `sys.stdout` with a custom stream that writes both to the original terminal AND an internal `io.StringIO` buffer.
- **Persistence:** Appends a single JSON object to `myptvlog.jsonl` in the current working directory upon exit.
- **Error Capture:** Catches unhandled exceptions, logs the full traceback, and updates the `status` field.

#### B. `workflow.workflow` (Modified Class)
- **`get_action_params(action)` (New Method):** Extracts a simple dictionary snapshot of parameters for the requested action from the internal Pandas DataFrame.
- **`__init__` (Modified Logic):** Wraps the action dispatching block (`if/elif/else`) within the `ActionLogger` context.

## 3. Data Specification (`myptvlog.jsonl`)

Each line in the log file is a standalone JSON object:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | `string` | ISO 8601 UTC timestamp of execution start. |
| `action` | `string` | The MyPTV operation name (e.g., "segmentation"). |
| `param_file` | `string` | Path to the `.yml` file used for this run. |
| `parameters` | `object` | Key-value pairs of all parameters for the action. |
| `status` | `string` | "success" or "failed". |
| `duration_seconds` | `float` | Wall-clock time from start to completion. |
| `output` | `string` | Full captured `stdout` (console messages). |
| `error` | `string` | The traceback string if `status` is "failed"; else `null`. |

## 4. Implementation Details

### 4.1 Tee Implementation
To achieve real-time terminal output while capturing to a buffer, we will implement a `Tee` class:
```python
class Tee:
    def __init__(self, original, buffer):
        self.original = original
        self.buffer = buffer
    def write(self, data):
        self.original.write(data)
        self.buffer.write(data)
    def flush(self):
        self.original.flush()
        self.buffer.flush()
```

### 4.2 Workflow Integration
The `workflow.py` file will require minimal changes to avoid upstream friction:
1. Import `ActionLogger` inside `__init__` or at module level.
2. Wrap the existing dispatch logic.

## 5. Success Criteria
- [ ] Running any action (e.g., `segmentation`) creates/appends to `myptvlog.jsonl`.
- [ ] Console output appears in the terminal immediately (not buffered until end).
- [ ] Crashing an action (e.g., bad parameter) still results in a "failed" log entry with the error message.
- [ ] The `myptvlog.jsonl` file is valid JSONL format and easily readable by AI tools.
