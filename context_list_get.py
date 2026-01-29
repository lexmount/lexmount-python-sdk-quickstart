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
set_log_level("DEBUG")

client = Lexmount()

def list_all_contexts():
    """List all contexts in the project."""
    print("\n" + "-" * 50)
    print("Listing all contexts...")
    print("-" * 50)

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


def main():
    """Demonstrate context list and get operations."""
    print("=" * 60)
    print("Context Management - List, Get & Delete Demo")
    print("=" * 60)

    created_contexts = []
    active_session = None

    try:
        # ============================================================
        # Step 1: Create two contexts
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 1: Create two contexts")
        print("=" * 60)

        # Create context 1
        print("\n   Creating context 1...")
        context1 = client.contexts.create(
            metadata={"name": "context_for_session", "purpose": "demo"}
        )
        created_contexts.append(context1.id)
        print(f"   ✓ Context 1 created: {context1.id}")

        # Create context 2
        print("\n   Creating context 2...")
        context2 = client.contexts.create(
            metadata={"name": "context_standalone", "purpose": "demo"}
        )
        created_contexts.append(context2.id)
        print(f"   ✓ Context 2 created: {context2.id}")

        # wait user input
        input("\n   Press Enter to continue...")

        # ============================================================
        # Step 2: Bind context 1 to a session (will be locked)
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 2: Bind context 1 to a session (will be locked)")
        print("=" * 60)

        print(f"\n   Creating session with context: {context1.id}")
        active_session = client.sessions.create(
            context={"id": context1.id, "mode": "read_write"}
        )
        print(f"   ✓ Session created: {active_session.id}")
        print(f"   Context 1 is now LOCKED by this session")

        # wait user input
        input("\n   Press Enter to continue...")

        # ============================================================
        # Step 3: List all contexts (should show 1 locked, 1 available)
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 3: List contexts (expect 1 locked, 1 available)")
        print("=" * 60)

        list_all_contexts()

        # Get details of both contexts
        print("\n   --- Context Details ---")
        get_context_details(context1.id)
        get_context_details(context2.id)

        # wait user input
        input("\n   Press Enter to continue...")

        # ============================================================
        # Step 4: Try to delete both contexts
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 4: Try to delete both contexts")
        print("=" * 60)

        # Try to delete context 1 (locked - should fail)
        print(f"\n   Attempting to delete context 1 (locked): {context1.id}")
        try:
            client.contexts.delete(context1.id)
            print("   ✓ Context 1 deleted (unexpected!)")
            created_contexts.remove(context1.id)
        except (APIError, ContextNotFoundError) as e:
            print(f"   ✗ Failed as expected: {e}")
            print("   (Cannot delete a locked context)")

        # Try to delete context 2 (available - should succeed)
        print(f"\n   Attempting to delete context 2 (available): {context2.id}")
        try:
            client.contexts.delete(context2.id)
            print("   ✓ Context 2 deleted successfully")
            created_contexts.remove(context2.id)
        except (APIError, ContextNotFoundError) as e:
            print(f"   ✗ Failed: {e}")

        # wait user input
        input("\n   Press Enter to continue...")

        # ============================================================
        # Step 5: List contexts again (should only show context 1)
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 5: List contexts again (expect only context 1)")
        print("=" * 60)

        list_all_contexts()

        # ============================================================
        # Step 6: Close session and cleanup
        # ============================================================
        print("\n" + "=" * 60)
        print("STEP 6: Close session and cleanup")
        print("=" * 60)

        print(f"\n   Closing session: {active_session.id}")
        active_session.close()
        active_session = None
        print("   ✓ Session closed, context 1 is now unlocked")

        # Now delete context 1
        if context1.id in created_contexts:
            print(f"\n   Now deleting context 1: {context1.id}")
            try:
                client.contexts.delete(context1.id)
                print("   ✓ Context 1 deleted successfully")
                created_contexts.remove(context1.id)
            except (APIError, ContextNotFoundError) as e:
                print(f"   ✗ Failed: {e}")

        # Final list
        print("\n" + "-" * 50)
        print("Final state:")
        list_all_contexts()

    except Exception as e:
        print(f"\n   ✗ Error: {e}")
        raise

    finally:
        # Cleanup: close session if still active
        if active_session:
            print("\n   [Cleanup] Closing active session...")
            active_session.close()

        # Cleanup: delete any remaining created contexts
        for ctx_id in created_contexts:
            print(f"\n   [Cleanup] Deleting context: {ctx_id}")
            try:
                client.contexts.delete(ctx_id)
                print(f"   ✓ Deleted")
            except Exception as e:
                print(f"   ✗ Failed to delete: {e}")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
