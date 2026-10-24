"""Shared configuration and result handling for the Browser Agent examples."""

import os
import sys
from quickstart_auth import ensure_credentials
from lexmount import APIError, RunWaitTimeout


def configuration():
    ensure_credentials()
    return dict(
        api_key=os.environ["LEXMOUNT_API_KEY"],
        project_id=os.environ["LEXMOUNT_PROJECT_ID"],
        base_url=os.getenv("LEXMOUNT_BASE_URL", "https://api.lexmount.com"),
    )


def report(run):
    print(
        {
            "id": run.id,
            "status": run.status,
            "created_request_id": run.created_request_id,
        }
    )
    if run.status == "succeeded":
        print(run.output)
    else:
        print(
            {
                "stop_reason": run.stop_reason,
                "error": run.error,
                "partial_output": run.output,
            }
        )
    # None means metering is pending, not zero cost.
    print(run.usage)
    return run.status == "succeeded"


def failure(error):
    def display(*values):
        print(*values, file=sys.stderr)

    if isinstance(error, RunWaitTimeout):
        display(
            f"Stopped waiting for {error.run_id}; the Run is still active. Resume with runs.get/wait.",
            error.request_id,
        )
    elif isinstance(error, APIError):
        display(
            {
                "status_code": error.status_code,
                "code": error.code,
                "request_id": error.request_id,
            }
        )
    else:
        display(str(error))
