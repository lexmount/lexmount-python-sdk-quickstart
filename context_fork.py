"""
Context fork quickstart example.

This example demonstrates:
- Creating a source context
- Forking it into a new context
- Querying the forked context details
- Cleaning up both source and forked contexts
"""
from dotenv import load_dotenv

load_dotenv(override=True)

from lexmount import ContextLockedError, ContextNotFoundError, Lexmount

client = Lexmount()


def main():
    source = None
    forked = None

    try:
        source = client.contexts.create(metadata={"scenario": "quickstart-context-fork"})
        print(f"Source context created: {source.id}")

        forked = client.contexts.fork(source.id)
        print(f"Forked context created: {forked.id}")

        details = client.contexts.get(forked.id)
        print(f"Forked context status: {details.status}")
    except ContextLockedError as error:
        print(f"Source context is locked: {error}")
        raise
    except ContextNotFoundError as error:
        print(f"Source context not found: {error}")
        raise
    finally:
        if forked is not None:
            client.contexts.delete(forked.id)
        if source is not None:
            client.contexts.delete(source.id)


if __name__ == "__main__":
    main()
