"""
Example: List and manage browser sessions

This example demonstrates how to:
1. List all active sessions
2. Display session information
3. Clean up sessions
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from lexmount import Lexmount

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Initialize client
client = Lexmount(
    api_key=os.getenv("LEXMOUNT_API_KEY"),
    project_id=os.getenv("LEXMOUNT_PROJECT_ID")
)

def main():
    print("=== Lexmount Session List Example ===\n")

    # Create a few test sessions
    print("1. Creating test sessions...")
    session1 = client.sessions.create(browser_mode="normal")
    print(f"   Created session 1: {session1.session_id}")

    session2 = client.sessions.create(browser_mode="normal")
    print(f"   Created session 2: {session2.session_id}")

    # List all sessions
    print("\n2. Listing all sessions...")
    result = client.sessions.list()
    print(f"   Found {len(result)} sessions on current page")
    print(f"   Pagination: total={result.pagination.total_count}, active={result.pagination.active_count}, closed={result.pagination.closed_count}")

    # List only active sessions (server-side filtering)
    print("\n3. Listing only active sessions...")
    active_result = client.sessions.list(status="active")
    print(f"   Found {len(active_result)} active sessions:\n")

    for i, session in enumerate(active_result.sessions, 1):
        print(f"   Session {i}:")
        print(f"     ID: {session.id}")
        print(f"     Status: {session.status}")
        print(f"     Browser Type: {session.browser_type}")
        print(f"     Created At: {session.created_at}")
        print(f"     Container ID: {session.container_id}")
        print(f"     WebSocket URL: {session.ws or 'N/A'}")
        print(f"     Inspect URL: {session.inspect_url}")
        if session.inspect_url_dbg:
            print(f"     Debug URL: {session.inspect_url_dbg}")
        print()

    # Clean up sessions
    print("4. Cleaning up sessions...")
    for session in result.sessions:
        try:
            client.sessions.delete(session_id=session.id)
            print(f"   Deleted session: {session.id}")
        except Exception as e:
            print(f"   Failed to delete session {session.id}: {e}")

    # Verify cleanup
    print("\n5. Verifying cleanup...")
    remaining_result = client.sessions.list()
    print(f"   Remaining sessions: {len(remaining_result)}")
    print(f"   Pagination: total={remaining_result.pagination.total_count}, active={remaining_result.pagination.active_count}")

    print("\n=== Example Complete ===")
    print("\nUsage tips:")
    print("  - Use list() to get all sessions with pagination info")
    print("  - Use list(status='active') for server-side filtering")
    print("  - Access sessions via result.sessions")
    print("  - Access pagination via result.pagination")
    print("  - Status values: 'active', 'closed', etc.")

if __name__ == "__main__":
    main()
