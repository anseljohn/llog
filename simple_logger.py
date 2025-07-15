import sys
import json
from datetime import datetime, timezone

def main(message=None):
    if message is None:
        if len(sys.argv) < 2:
            print("Usage: python simple_logger.py <message>")
            sys.exit(1)
        message = " ".join(sys.argv[1:])
    now = datetime.now(timezone.utc)
    iso_time = now.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    output = {
        "message": message,
        "datetime": iso_time
    }
    return output

if __name__ == "__main__":
    result = main()
    print(json.dumps(result))