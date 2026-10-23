import json
import math
import os
from pathlib import Path
import sys
import time
import uuid
from urllib.parse import urlsplit
from lexmount import Lexmount
from browser_agent_common import configuration, report, failure


def persist(path, job):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as output:
        json.dump(job, output, indent=2)
        output.flush()
        os.fsync(output.fileno())


def sync_directory(path):
    if os.name == "nt":
        return
    descriptor = os.open(path.resolve().parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def main():
    config = configuration()
    url = urlsplit(config["base_url"])
    scope = {
        "project_id": config["project_id"],
        "api_origin": url.scheme.lower()
        + "://"
        + (
            url.netloc.lower()[:-4]
            if url.netloc.lower().endswith(":443")
            else url.netloc.lower()
        ),
    }
    path = Path(os.getenv("BROWSER_AGENT_JOB_FILE", "browser-agent-job.json"))
    try:
        job = json.loads(path.read_text())
    except FileNotFoundError:
        business_id = str(uuid.uuid4())
        job = {
            **scope,
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
        persist(path, job)
        sync_directory(path)
    if not isinstance(job, dict) or any(
        job.get(key) != value for key, value in scope.items()
    ):
        raise ValueError(
            "Recovery record has no matching Project ID/API origin. Reconcile it in its original project and service; do not reuse it here."
        )
    key = job.get("idempotency_key")
    if (
        not isinstance(job.get("business_id"), str)
        or not job["business_id"]
        or not isinstance(key, str)
        or not 1 <= len(key) <= 128
        or any(ord(c) < 33 or ord(c) > 126 for c in key)
        or not isinstance(job.get("request"), dict)
        or "run_id" not in job
        or (
            job["run_id"] is not None
            and (not isinstance(job["run_id"], str) or not job["run_id"].strip())
        )
    ):
        raise ValueError(
            "Invalid recovery record. Reconcile the original request before creating another task."
        )
    with Lexmount(**config) as client:
        api = client.browser_agent
        if not job["run_id"]:
            created = job.get("created_at")
            age = (
                time.time() - created if type(created) in (int, float) else float("nan")
            )
            if not math.isfinite(age) or age < 0 or age >= 7 * 86400:
                raise ValueError(
                    "The recovery key is outside its 7-day window. Reconcile the original request before creating another task."
                )
            receipt = api.runs.create(
                **job["request"], idempotency_key=job["idempotency_key"]
            )
            job["run_id"] = receipt.id
            temporary = path.with_name(path.name + "." + str(uuid.uuid4()) + ".tmp")
            persist(temporary, job)
            os.replace(temporary, path)
            sync_directory(path)
        # A known Run is only queried, never created again after a restart.
        print("Business job:", job["business_id"], "Run:", job["run_id"])
        return 0 if report(api.runs.wait(job["run_id"])) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        failure(error)
        sys.exit(1)
