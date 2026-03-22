import json
import os

def reorder_log_fields(log_path):
    if not os.path.exists(log_path):
        print(f"File not found: {log_path}")
        return

    updated_lines = []
    with open(log_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                
                # Desired field order:
                # 1. timestamp
                # 2. comment (if present)
                # 3. action
                # ... then everything else
                
                new_entry = {}
                if "timestamp" in entry:
                    new_entry["timestamp"] = entry.pop("timestamp")
                if "comment" in entry:
                    new_entry["comment"] = entry.pop("comment")
                
                # Add all remaining keys
                new_entry.update(entry)
                
                updated_lines.append(json.dumps(new_entry))
            except json.JSONDecodeError:
                updated_lines.append(line.strip())

    with open(log_path, 'w') as f:
        for line in updated_lines:
            f.write(line + '\n')
    
    print(f"Successfully reordered fields in {log_path}")

if __name__ == "__main__":
    reorder_log_fields("Data/20260315_frames/myptvlog.jsonl")
