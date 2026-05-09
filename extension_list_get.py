"""
Extension list, get, upload, and delete example.

This example demonstrates:
- Listing all extensions in the project
- Getting details of a specific extension
- Uploading a new extension archive
- Deleting extensions
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from lexmount import APIError, Lexmount, set_log_level

load_dotenv(override=True)

set_log_level("WARNING")

client = Lexmount()


def list_all_extensions():
    """List all extensions in the project."""
    try:
        extensions = client.extensions.list(limit=100)
        print(f"Total extensions found: {len(extensions)}")

        if not extensions:
            print("   No extensions found.")
            return

        for extension in extensions:
            print(f"\n   ✅ Extension ID: {extension.id}")
            print(f"      Name: {extension.name}")
            print(f"      Project ID: {extension.project_id}")
            if extension.created_at:
                print(f"      Created: {extension.created_at}")
            if extension.updated_at:
                print(f"      Updated: {extension.updated_at}")
    except APIError as error:
        print(f"   ✗ Failed to list extensions: {error}")
        print("   (Service may be temporarily unavailable, please retry)")


def get_extension_details(extension_id: str):
    """Get detailed information about a specific extension."""
    print(f"\n   Getting details for extension: {extension_id}")

    try:
        extension = client.extensions.get(extension_id)
        print(f"      Name: {extension.name}")
        print(f"      Project ID: {extension.project_id}")
        if extension.created_at:
            print(f"      Created: {extension.created_at}")
        if extension.updated_at:
            print(f"      Updated: {extension.updated_at}")
        return extension
    except APIError as error:
        print(f"      ✗ Failed to get extension: {error}")
        return None


def upload_extension(file_path: str, name: Optional[str] = None):
    """Upload an extension archive."""
    archive_path = Path(file_path).expanduser().resolve()
    if not archive_path.exists():
        print(f"   ✗ Extension file not found: {archive_path}")
        return None

    try:
        extension = client.extensions.upload(str(archive_path), name=name)
        print(f"   ✓ Uploaded extension: {extension.id}")
        print(f"      Name: {extension.name}")
        return extension
    except APIError as error:
        print(f"   ✗ Failed to upload extension: {error}")
        return None


def delete_extension(extension_id: str):
    """Delete a specific extension."""
    try:
        client.extensions.delete(extension_id)
        print(f"   ✓ Deleted extension: {extension_id}")
    except APIError as error:
        print(f"   ✗ Failed to delete extension {extension_id}: {error}")


def delete_all_extensions():
    """List all extensions and delete each one."""
    try:
        extensions = client.extensions.list(limit=100)
        if not extensions:
            print("   No extensions to delete.")
            return

        print(f"   Found {len(extensions)} extension(s). Deleting...")
        deleted = 0
        failed = 0

        for extension in extensions:
            try:
                client.extensions.delete(extension.id)
                print(f"   ✓ Deleted: {extension.id}")
                deleted += 1
            except APIError as error:
                print(f"   ✗ Failed to delete {extension.id}: {error}")
                failed += 1

        print(f"\n   Done: {deleted} deleted, {failed} failed.")
    except APIError as error:
        print(f"   ✗ Failed to list extensions: {error}")
        raise


def main():
    """Demonstrate extension list/get/upload/delete operations."""
    parser = argparse.ArgumentParser(description="Extension list, get, upload & delete demo")
    parser.add_argument(
        "--extension-id",
        type=str,
        metavar="ID",
        help="Show details for the given extension ID",
    )
    parser.add_argument(
        "--upload",
        type=str,
        metavar="FILE",
        help="Upload the given zip/crx extension archive",
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Optional name to use with --upload",
    )
    parser.add_argument(
        "--delete-id",
        type=str,
        metavar="ID",
        help="Delete the given extension ID",
    )
    parser.add_argument(
        "--delete-all",
        action="store_true",
        help="Delete all extensions in the current project",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Extension Management - List, Get, Upload & Delete Demo")
    print("=" * 60)

    try:
        if args.upload:
            upload_extension(args.upload, args.name)
            return

        if args.delete_id:
            delete_extension(args.delete_id)
            return

        if args.delete_all:
            delete_all_extensions()
            return

        if args.extension_id:
            get_extension_details(args.extension_id)
            return

        list_all_extensions()
    except Exception as error:
        print(f"   ✗ Failed: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
