"""Read current and historical WebFetch usage without creating browser sessions."""
import json
import os
import sys
import time
from dataclasses import asdict

from quickstart_auth import ensure_credentials
from lexmount import Lexmount


def main():
    ensure_credentials()
    with Lexmount(
        api_key=os.environ["LEXMOUNT_API_KEY"],
        project_id=os.environ["LEXMOUNT_PROJECT_ID"],
        base_url=os.getenv("LEXMOUNT_BASE_URL", "https://api.lexmount.com"),
    ) as client:
        if not hasattr(client, "usage"):
            raise RuntimeError(
                "This SDK has no usage resource. Install the usage-enabled SDK described in README."
            )
        current = client.usage.current(with_response=True)
        print(json.dumps({"endpoint": "current", "request_id": current.request_id,
                          "status_code": current.status_code, "data": asdict(current.data)}, indent=2))
        time.sleep(1.1)
        history = client.usage.history(with_response=True)
        print(json.dumps({"endpoint": "history", "request_id": history.request_id,
                          "status_code": history.status_code, "data": asdict(history.data)}, indent=2))
        unavailable = sum(period.usage is None for period in history.data.periods)
        print(f"Periods outside retention: {unavailable} (null usage is not zero).")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Do not dump request objects/headers: they can contain API keys.
        if hasattr(error, "status_code"):
            print("Usage request failed:", error.status_code,
                  getattr(error, "code", None), getattr(error, "request_id", None), file=sys.stderr)
        else:
            print(str(error), file=sys.stderr)
        sys.exit(1)
