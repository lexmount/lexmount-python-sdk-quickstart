import os
import sys
import uuid
from lexmount import Lexmount
from browser_agent_common import configuration, report, failure


def main():
    with Lexmount(**configuration()) as client:
        receipt = client.browser_agent.runs.create(
            query=os.getenv(
                "BROWSER_AGENT_QUERY", "Read the page title and summarize the page."
            ),
            start_url=os.getenv("BROWSER_AGENT_START_URL", "https://example.com/"),
            idempotency_key=os.getenv("RUN_IDEMPOTENCY_KEY") or str(uuid.uuid4()),
        )
        print("Accepted (not yet completed):", receipt.id)
        return 0 if report(client.browser_agent.runs.wait(receipt.id)) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        failure(error)
        sys.exit(1)
