import json
import os
import sys
import shutil
import tempfile

def migrate_log(log_path):
    if not os.path.exists(log_path):
        print(f"Error: File {log_path} not found.", file=sys.stderr)
        sys.exit(1)

    # Create a backup
    backup_path = log_path + ".bak"
    shutil.copy2(log_path, backup_path)
    
    try:
        # Use a temporary file to write the updated content
        fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(log_path), text=True)
        with os.fdopen(fd, 'w') as temp_file:
            with open(log_path, 'r') as original_file:
                for line in original_file:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if "comment" not in data:
                            data["comment"] = ""
                        temp_file.write(json.dumps(data) + "\n")
                    except json.JSONDecodeError:
                        print(f"Error: Malformed JSON line: {line}", file=sys.stderr)
                        # Keep the original malformed line as per requirements
                        temp_file.write(line + "\n")
        
        # Replace original file with the updated one
        shutil.move(temp_path, log_path)
        print(f"Successfully migrated {log_path}. Backup created at {backup_path}")

    except Exception as e:
        print(f"An error occurred during migration: {e}", file=sys.stderr)
        # Restore from backup if something went wrong
        shutil.copy2(backup_path, log_path)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python migrate_log_comments.py <log_file_path>", file=sys.stderr)
        sys.exit(1)
    
    migrate_log(sys.argv[1])
