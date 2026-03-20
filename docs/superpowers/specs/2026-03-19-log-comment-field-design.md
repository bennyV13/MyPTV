# Design Spec: MyPTV Logging - Adding Comment Field

## Overview
This design specifies the addition of a `comment` field to all log entries in `myptvlog.jsonl` files and the update of the `ActionLogger` class to support this field for future entries.

## 1. Architecture & Components
- **Migration Utility:** A one-time Python script `scripts/migrate_log_comments.py` that will iterate through existing log files and add the `comment` key with a default value.
- **Core Library Update:** Modifying the `ActionLogger` class in `MyPTV/myptv/logging_utils.py` to allow users to provide a `comment` when starting a logged action.

## 2. Migration Logic (`scripts/migrate_log_comments.py`)
- **Input:** Path to `myptvlog.jsonl`.
- **Process:**
  - Create a backup of the original file (`.bak`).
  - Read the file line-by-line.
  - Parse each line as a JSON object.
  - If the line is malformed, log an error and skip or handle gracefully.
  - If the `"comment"` key is missing, add `"comment": ""`.
  - Write the updated JSON object back to a temporary file.
- **Output:** The original `myptvlog.jsonl` will be replaced with the updated content after verification.

## 3. Library Update (`MyPTV/myptv/logging_utils.py`)
- **ActionLogger.__init__:**
  - Add a new parameter `comment=""`.
  - Store it as `self.comment`.
- **ActionLogger.__exit__:**
  - Include `"comment": self.comment` in the `log_entry` dictionary.
  - Ensure the field order is logical (e.g., after `status` or `duration_seconds`).

## 4. Testing & Verification
### Automated Tests
- Create a test file `MyPTV/tests/test_logging_comment.py`.
- Mock the log file path and run `ActionLogger` with various comment values.
- Assert the resulting JSON contains the `comment` field with the expected value.
- **Idempotency Test:** Verify that running the migration script twice does not duplicate fields or corrupt the file.
- **Error Handling Test:** Verify the script handles malformed JSON lines without crashing.

### Manual Verification
- Run the migration script on `Data/20260315_frames/myptvlog.jsonl`.
- Verify the first few entries using `head -n 5 Data/20260315_frames/myptvlog.jsonl | jq`.
- Run a sample action (e.g., `python workflow.py help --comment "test comment"`) and confirm it's logged with the provided comment.

## 5. Deployment Plan
- Use a sub-agent in an isolated worktree for the migration and code changes.
- Final action: Stage and commit changes to the `logger` branch.
