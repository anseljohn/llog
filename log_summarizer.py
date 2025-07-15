import openai
import os
import sys
from datetime import datetime, timedelta

LOG_BASE_DIR = os.path.expanduser("~/.llog/logs")

def summarize_logs(log_paths, openai_client):
    """
    Loads log entries from the given list of JSON file paths, and uses the OpenAI client to summarize them.
    Returns a concise, grouped rundown as plain text, grouping by task similarity and time proximity.
    """
    logs = []
    for path in log_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                log = f.read()
                # Try to parse as JSON
                import json
                logs.append(json.loads(log))
        except Exception as e:
            continue  # skip unreadable or malformed files

    if not logs:
        return "No logs to summarize."

    # Compose a prompt for a grouped, concise rundown
    log_texts = []
    for log in logs:
        dt = log.get("datetime", "")
        msg = log.get("message", "")
        log_texts.append(f"[{dt}] {msg}")
    joined_logs = "\n".join(log_texts)

    system_prompt = (
        "You are a helpful assistant that summarizes a list of log entries. "
        "Group related log entries by task similarity and by time proximity (e.g., logs close together in time). "
        "For each group, provide a short label (topic or task) and, if possible, a time range. "
        "Under each group, provide a bulleted list of the relevant log points. "
        "Start with a one-sentence overall summary. Be brief, clear, and actionable."
    )
    user_prompt = (
        f"Here are the logs:\n{joined_logs}\n\nSummary:"
    )

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=600,
        temperature=0.3
    )
    content = response.choices[0].message.content.strip()
    return content


def infer_date_range_from_query(query, openai_client):
    """
    Uses OpenAI to infer a strict date range keyword from a natural language query.
    Returns one of: "today", "this month", "this year", "last hour", "last month", etc.
    openai_client: an OpenAI client instance with a .chat.completions.create() method.
    """
    system_prompt = (
        "You are a helpful assistant that maps natural language time queries to one of the following strict date range keywords: "
        "\"today\", \"this month\", \"this year\", \"last hour\", \"last month\", \"last week\", \"yesterday\", \"this minute\", \"last minute\". "
        "Given a user query, respond with only the most appropriate keyword from this list. "
        "If the query is ambiguous, pick the closest match. Do not explain your answer."
    )
    user_prompt = f"User query: \"{query}\""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=10,
        temperature=0
    )
    # Extract the keyword from the response
    keyword = response.choices[0].message.content.strip().lower()
    # Optionally, validate the keyword
    allowed_keywords = {
        "today", "this month", "this year", "last hour", "last month", "last week", "yesterday", "this minute", "last minute"
    }
    if keyword in allowed_keywords:
        return keyword
    # Try to extract a valid keyword from the response if extra text is present
    for k in allowed_keywords:
        if k in keyword:
            return k
    # If nothing matches, default to "today"
    return "today"


def get_log_files_for_range(date_range):
    """
    Returns a list of log file paths matching the given date range.
    date_range: str, one of "today", "this month", "this year", "last hour", "this minute", "last minute"
    """
    now = datetime.now()
    files = []

    if date_range == "today":
        dir_path = os.path.join(LOG_BASE_DIR, f"{now.year}/{now.month:02d}/{now.day:02d}")
        if os.path.exists(dir_path):
            for fname in os.listdir(dir_path):
                if fname.endswith(".json"):
                    files.append(os.path.join(dir_path, fname))
    elif date_range == "last month":
        month_dir = os.path.join(LOG_BASE_DIR, f"{now.year}/{now.month:02d}")
        if os.path.exists(month_dir):
            # All day subdirs in this month
            for entry in os.listdir(month_dir):
                day_dir = os.path.join(month_dir, entry)
                if os.path.isdir(day_dir):
                    for fname in os.listdir(day_dir):
                        if fname.endswith(".json"):
                            files.append(os.path.join(day_dir, fname))
    elif date_range == "this year":
        year_dir = os.path.join(LOG_BASE_DIR, f"{now.year}")
        if os.path.exists(year_dir):
            # All month/day subdirs in this year
            for month_entry in os.listdir(year_dir):
                month_dir = os.path.join(year_dir, month_entry)
                if os.path.isdir(month_dir):
                    for day_entry in os.listdir(month_dir):
                        day_dir = os.path.join(month_dir, day_entry)
                        if os.path.isdir(day_dir):
                            for fname in os.listdir(day_dir):
                                if fname.endswith(".json"):
                                    files.append(os.path.join(day_dir, fname))
    elif date_range in ("last hour", "last hour or so"):
        # Find all logs in the last 70 minutes (to be generous)
        cutoff = now - timedelta(minutes=70)
        # Traverse all year/month/day dirs
        for year in os.listdir(LOG_BASE_DIR):
            year_path = os.path.join(LOG_BASE_DIR, year)
            if not os.path.isdir(year_path):
                continue
            for month in os.listdir(year_path):
                month_path = os.path.join(year_path, month)
                if not os.path.isdir(month_path):
                    continue
                for day in os.listdir(month_path):
                    day_path = os.path.join(month_path, day)
                    if not os.path.isdir(day_path):
                        continue
                    for fname in os.listdir(day_path):
                        if not fname.endswith(".json"):
                            continue
                        try:
                            # Filename format: HHMMSS_micro.json
                            time_part = fname.split("_")[0]
                            hour = int(time_part[:2])
                            minute = int(time_part[2:4])
                            second = int(time_part[4:6])
                            file_date = datetime(
                                int(year), int(month), int(day),
                                hour, minute, second
                            )
                            if file_date >= cutoff:
                                files.append(os.path.join(day_path, fname))
                        except Exception:
                            continue
    elif date_range == "this minute":
        # Find all logs in the current minute
        dir_path = os.path.join(LOG_BASE_DIR, f"{now.year}/{now.month:02d}/{now.day:02d}")
        if os.path.exists(dir_path):
            for fname in os.listdir(dir_path):
                if not fname.endswith(".json"):
                    continue
                try:
                    # Filename format: HHMMSS_micro.json
                    time_part = fname.split("_")[0]
                    hour = int(time_part[:2])
                    minute = int(time_part[2:4])
                    # Only include logs from the current hour and minute
                    if hour == now.hour and minute == now.minute:
                        files.append(os.path.join(dir_path, fname))
                except Exception:
                    continue
    elif date_range == "last minute":
        # Find all logs in the last 2 minutes (to be generous)
        cutoff = now - timedelta(minutes=2)
        # Traverse all year/month/day dirs
        for year in os.listdir(LOG_BASE_DIR):
            year_path = os.path.join(LOG_BASE_DIR, year)
            if not os.path.isdir(year_path):
                continue
            for month in os.listdir(year_path):
                month_path = os.path.join(year_path, month)
                if not os.path.isdir(month_path):
                    continue
                for day in os.listdir(month_path):
                    day_path = os.path.join(month_path, day)
                    if not os.path.isdir(day_path):
                        continue
                    for fname in os.listdir(day_path):
                        if not fname.endswith(".json"):
                            continue
                        try:
                            # Filename format: HHMMSS_micro.json
                            time_part = fname.split("_")[0]
                            hour = int(time_part[:2])
                            minute = int(time_part[2:4])
                            second = int(time_part[4:6])
                            file_date = datetime(
                                int(year), int(month), int(day),
                                hour, minute, second
                            )
                            if file_date >= cutoff:
                                files.append(os.path.join(day_path, fname))
                        except Exception:
                            continue
    else:
        raise ValueError(f"Unknown date_range: {date_range}")

    return sorted(files)

def main():
    if len(sys.argv) < 2:
        print("Usage: python log_summarizer.py <date_range>")
        print("date_range: today | this month | this year | last hour | this minute | last minute")
        sys.exit(1)
    user_input = " ".join(sys.argv[1:]).strip().lower()
    try:
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        date_range = infer_date_range_from_query(user_input, client)
        log_files = get_log_files_for_range(date_range)
        if not log_files:
            print(f"No log files found for range: {date_range}")
        else:
            summary = summarize_logs(log_files, client)
            print(summary)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()