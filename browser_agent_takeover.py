"""Handle a manual pause or an assistance request on an existing v2 run."""

import os
import sys
import time

from lexmount import Lexmount

from browser_agent_common import configuration, failure


def main():
    config = configuration()
    run_id = os.getenv("RUN_ID", "").strip()
    if not run_id:
        raise ValueError("Set RUN_ID to an existing Browser Agent v2 run.")
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise ValueError("Run this example in a private terminal.")

    with Lexmount(**config) as client:
        runs = client.browser_agent.v2.runs
        run = runs.get(run_id)
        if run.status == "running":
            run = runs.pause(run_id)
        for _ in range(30):
            if run.status not in ("pausing", "running"):
                break
            time.sleep(1)
            run = runs.get(run_id)

        if run.status == "paused" and run.pause and run.preview_url:
            input(f"Open {run.preview_url} and press Enter after finishing: ")
            run = runs.resume(run_id, run.pause.id)
        elif run.status == "waiting_for_human" and run.intervention:
            help_request = run.intervention
            print(help_request.instructions)
            if help_request.url:
                print(help_request.url)
            outcome = input("Enter resolved or unresolved: ").strip()
            if outcome not in ("resolved", "unresolved"):
                raise ValueError("Invalid outcome.")
            response = input("Brief response: ").strip() if help_request.response_required else None
            if help_request.response_required and not response:
                raise ValueError("A response is required.")
            run = runs.complete_intervention(
                run_id, help_request.id, outcome=outcome, response=response
            )
        else:
            print(f"No handoff available (status: {run.status}).")
            return
        print(f"Run {run.id}: {run.status}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        failure(error)
        sys.exit(1)
