#!/usr/bin/env python3
import simple_logger
import os
import json
import sys
import shutil
import tempfile
import subprocess
from datetime import datetime

LOG_BASE_DIR = os.path.expanduser("~/.wlog/logs")

EDITOR = os.environ.get("EDITOR", "vim")

def reset_logs():
    if os.path.exists(LOG_BASE_DIR):
        shutil.rmtree(LOG_BASE_DIR)
        print(f"All logs deleted from {LOG_BASE_DIR}")
    else:
        print(f"No logs to delete at {LOG_BASE_DIR}")

def log_message(message):
    log = simple_logger.main(message)
    dt = datetime.fromisoformat(log["datetime"])
    log_dir = os.path.join(
        LOG_BASE_DIR, f"{dt.year}/{dt.month:02d}/{dt.day:02d}"
    )
    os.makedirs(log_dir, exist_ok=True)
    filename = f"{dt.strftime('%H%M%S_%f')}.json"
    filepath = os.path.join(log_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"Logged: {log['message']}")

def log_interactive():
    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False, mode="w+", encoding="utf-8") as tf:
        tf.write("# Enter your log message below. Lines starting with '#' will be ignored.\n")
        tf.flush()
        subprocess.call([EDITOR, tf.name])
        tf.seek(0)
        lines = tf.readlines()
    os.unlink(tf.name)
    print("DEBUG: raw lines:", repr(lines))  # Debug
    # Remove comment lines and join
    filtered_lines = []
    for line in lines:
        if line.strip().startswith("#"):
            continue
        filtered_lines.append(line.rstrip("\n"))
    print("DEBUG: filtered lines:", repr(filtered_lines))  # Debug
    message = "\n".join(filtered_lines).strip()
    print("DEBUG: final message:", repr(message))  # Debug
    if not message:
        print("Aborted: Empty log message.")
        sys.exit(1)
    log_message(message)

def summarize_logs_cli(date_range):
    import log_summarizer
    import openai
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    date_range = log_summarizer.infer_date_range_from_query(date_range, client)
    log_files = log_summarizer.get_log_files_for_range(date_range)
    if not log_files:
        print(f"No log files found for range: {date_range}")
    else:
        summary = log_summarizer.summarize_logs(log_files, client)
        print(summary)

def print_usage():
    print("Usage:")
    print("  wlog <message>                # Log a message")
    print("  wlog -i                       # Open editor for a detailed log message")
    print("  wlog --summarize <range>      # Summarize logs for a range (e.g. 'today', 'this month', 'this week')")
    print("  wlog --reset                  # Delete all logs")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    if sys.argv[1] == "--reset":
        reset_logs()
        sys.exit(0)
    elif sys.argv[1] == "--summarize":
        if len(sys.argv) < 3:
            print("Please provide a date range to summarize (e.g. 'today', 'this month', 'this week').")
            sys.exit(1)
        summarize_logs_cli(" ".join(sys.argv[2:]))
        sys.exit(0)
    elif sys.argv[1] == "-i":
        log_interactive()
        sys.exit(0)
    else:
        # Treat all args as the message
        log_message(" ".join(sys.argv[1:]))
