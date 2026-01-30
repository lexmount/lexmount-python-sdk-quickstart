"""
Context List and Get operations example.

This example demonstrates:
- Creating contexts
- Binding a context to a session (locked status)
- Listing all contexts in the project
- Getting details of a specific context
- Deleting contexts (success and failure cases)
"""
from lexmount import Lexmount, ContextNotFoundError, APIError, set_log_level
from dotenv import load_dotenv
from pathlib import Path
import argparse
import sys

load_dotenv(override=True)

# Set logging level (use DEBUG to see detailed request/response)
set_log_level("WARNING")

client = Lexmount()

def list_all_contexts():
    """List all contexts in the project."""

    try:
        contexts = client.contexts.list()
        print(f"Total contexts found: {len(contexts)}")

        if len(contexts) == 0:
            print("   No contexts found.")
            return

        for ctx in contexts:
            status_icon = "🔒" if ctx.is_locked() else "✅"
            print(f"\n   {status_icon} Context ID: {ctx.id}")
            print(f"      Status: {ctx.status}")
            if ctx.created_at:
                print(f"      Created: {ctx.created_at}")
            if ctx.updated_at:
                print(f"      Updated: {ctx.updated_at}")
    except APIError as e:
        print(f"   ✗ Failed to list contexts: {e}")
        print("   (Service may be temporarily unavailable, please retry)")


def get_context_details(context_id: str):
    """Get detailed information about a specific context."""
    print(f"\n   Getting details for context: {context_id}")

    try:
        ctx = client.contexts.get(context_id)
        print(f"      Status: {ctx.status}")
        if ctx.is_locked():
            print(f"      🔒 Locked")
        else:
            print(f"      ✅ Available")
        if ctx.created_at:
            print(f"      Created: {ctx.created_at}")
        if ctx.updated_at:
            print(f"      Updated: {ctx.updated_at}")
        return ctx
    except ContextNotFoundError:
        print(f"      ✗ Context not found")
        return None


def delete_all_contexts():
    """List all contexts and delete each one that is not locked."""
    try:
        contexts = client.contexts.list()
        if not contexts:
            print("   No contexts to delete.")
            return
        print(f"   Found {len(contexts)} context(s). Deleting unlocked ones...")
        deleted = 0
        skipped_locked = 0
        failed = 0
        for ctx in contexts:
            if ctx.is_locked():
                print(f"   ⏭ Skipped (locked): {ctx.id}")
                skipped_locked += 1
                continue
            try:
                client.contexts.delete(ctx.id)
                print(f"   ✓ Deleted: {ctx.id}")
                deleted += 1
            except Exception as e:
                print(f"   ✗ Failed to delete {ctx.id}: {e}")
                failed += 1
        print(f"\n   Done: {deleted} deleted, {skipped_locked} skipped (locked), {failed} failed.")
    except APIError as e:
        print(f"   ✗ Failed to list contexts: {e}")
        raise


def main():
    """Demonstrate context list and get operations."""
    parser = argparse.ArgumentParser(description="Context list, get & delete demo")
    parser.add_argument(
        "--delete-all",
        action="store_true",
        help="List all contexts and delete every unlocked one",
    )
    parser.add_argument(
        "--context-id",
        type=str,
        metavar="ID",
        help="Show details for the given context ID",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Context Management - List, Get & Delete Demo")
    print("=" * 60)

    created_contexts = []
    active_session = None

    if args.delete_all:
        try:
            delete_all_contexts()
        except Exception as e:
            print(f"   ✗ Failed: {e}")
            print("   (Service may be temporarily unavailable, please retry)")
            sys.exit(1)
        return

    if args.context_id:
        try:
            get_context_details(args.context_id)
        except Exception as e:
            print(f"   ✗ Failed to get context details: {e}")
            sys.exit(1)
        return

    try:
        list_all_contexts()
    except Exception as e:
        print(f"   ✗ Failed to list contexts: {e}")
        print("   (Service may be temporarily unavailable, please retry)")


if __name__ == "__main__":
    main()
