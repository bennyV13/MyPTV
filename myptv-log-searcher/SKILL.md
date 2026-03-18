---
name: myptv-log-searcher
description: Searches and analyzes MyPTV operation logs (myptvlog.jsonl) to retrieve past parameters, actions, and timestamps. Use this when a user asks about previous runs, wants to compare parameters between experiments, or needs to recover settings used for a specific calibration or segmentation.
---

# MyPTV Log Searcher

This skill helps you navigate and extract insights from `myptvlog.jsonl` files.

## Workflow

1. **Locate Logs**: Search for `myptvlog.jsonl` in the current workspace or known data directories (e.g., `Data/20260315_frames/myptvlog.jsonl`).
2. **Search Strategy**:
   - Use `grep_search` to find specific actions (e.g., `"action": "segmentation"`) or parameter values.
   - Use `read_file` to inspect the last few entries for the most recent state.
3. **Analysis**:
   - Compare "parameters" blocks between entries to identify changes in workflow.
   - Look for the "timestamp" to reconstruct the timeline of an experiment.

## Common Queries

- **Recent Actions**: `grep_search(pattern='{"timestamp"', file_path='path/to/myptvlog.jsonl')` and look at the tail.
- **Find Specific Params**: `grep_search(pattern='"threshold": "70"', file_path='path/to/myptvlog.jsonl')`.
- **Action History**: `grep_search(pattern='"action": "initial_calibration"', file_path='path/to/myptvlog.jsonl')`.

## Data Format

Logs are in JSONL (JSON Lines) format:
`{"timestamp": "ISO-DATE", "action": "ACTION_NAME", "parameters": {...}, "param_file": "PATH"}`
