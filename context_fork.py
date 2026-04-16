"""
Context fork quickstart example.

This example demonstrates:
- Accepting an existing source context id
- Forking it into a new context
- Printing the forked context id
"""
import argparse
from dotenv import load_dotenv

load_dotenv(override=True)

from lexmount import ContextLockedError, ContextNotFoundError, Lexmount

client = Lexmount()


def main():
    parser = argparse.ArgumentParser(description="Fork an existing context and print the new context id")
    parser.add_argument("context_id", help="Existing source context id")
    args = parser.parse_args()

    try:
        forked = client.contexts.fork(args.context_id)
        print(f"Forked context id: {forked.id}")
    except ContextLockedError as error:
        print(f"Source context is locked: {error}")
        raise
    except ContextNotFoundError as error:
        print(f"Source context not found: {error}")
        raise


if __name__ == "__main__":
    main()
