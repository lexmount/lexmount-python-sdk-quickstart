import os
import sys
import uuid
from lexmount import Lexmount
from browser_agent_common import configuration, report, failure


def main():
    with Lexmount(**configuration()) as client:
        api = client.browser_agent
        agent = api.agents.create(
            name="Page summary",
            instruction="Read the page and summarize its {{topic}}.",
            start_url="https://example.com/",
            output_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                },
                "required": ["title", "summary"],
                "additionalProperties": False,
            },
            idempotency_key=os.getenv("AGENT_IDEMPOTENCY_KEY") or str(uuid.uuid4()),
        )
        print("Saved Agent:", agent.id, "revision:", agent.revision)
        receipt = api.runs.create(
            agent_id=agent.id,
            variables={"topic": "main purpose"},
            metadata={"example": "structured-summary"},
            idempotency_key=os.getenv("RUN_IDEMPOTENCY_KEY") or str(uuid.uuid4()),
        )
        run = api.runs.wait(receipt.id)
        ok = report(run)
        if ok and isinstance(run.output, dict):
            print("Title:", run.output["title"])  # Already a dict; do not json.loads.
        return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        failure(error)
        sys.exit(1)
