import json
import os
from pathlib import Path
import sys
import time
import uuid
from lexmount import Lexmount
from browser_agent_common import configuration, report, failure


def main():
    path = Path(os.getenv("BROWSER_AGENT_JOB_FILE", "browser-agent-job.json"))
    try:
        job = json.loads(path.read_text())
    except FileNotFoundError:
        business_id = str(uuid.uuid4())
        job = {
            "business_id": business_id,
            "idempotency_key": "browser-agent:" + business_id,
            "created_at": time.time(),
            "request": {
                "query": "Read the page title.",
                "start_url": "https://example.com/",
                "metadata": {"business_id": business_id},
            },
            "run_id": None,
        }
        # Persist BEFORE POST. Exclusive creation prevents overwriting another job.
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as output:
            json.dump(job, output, indent=2)
    with Lexmount(**configuration()) as client:
        api = client.browser_agent
        if not job["run_id"]:
            if time.time() - job["created_at"] >= 7 * 86400:
                raise ValueError(
                    "The recovery key is outside its 7-day window. Reconcile the original request before creating another task."
                )
            receipt = api.runs.create(
                **job["request"], idempotency_key=job["idempotency_key"]
            )
            job["run_id"] = receipt.id
            temporary = path.with_name(path.name + "." + str(uuid.uuid4()) + ".tmp")
            descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w") as output:
                json.dump(job, output, indent=2)
            os.replace(temporary, path)
        # A known Run is only queried, never created again after a restart.
        print("Business job:", job["business_id"], "Run:", job["run_id"])
        return 0 if report(api.runs.wait(job["run_id"])) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        failure(error)
        sys.exit(1)
