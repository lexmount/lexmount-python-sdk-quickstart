"""
Example: List browser sessions across catalog regions.

This example demonstrates how to:
1. Load Lexmount credentials from .env
2. Read the public endpoint catalog
3. List active sessions from each catalog region and print their region
"""
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from lexmount import Lexmount

load_dotenv(override=True)

API_KEY = os.getenv("LEXMOUNT_API_KEY")
PROJECT_ID = os.getenv("LEXMOUNT_PROJECT_ID")
BASE_URL = os.getenv("LEXMOUNT_BASE_URL")


def create_client(region=None):
    return Lexmount(
        api_key=API_KEY,
        project_id=PROJECT_ID,
        base_url=BASE_URL,
        region=region,
    )


def catalog_regions(client):
    catalog = client.catalog_info()
    if not catalog.get("available"):
        return []

    return [
        region
        for region in catalog.get("regions", [])
        if region.get("region_id") and region.get("host")
    ]


def host_from_url(value):
    if not value:
        return None
    parsed = urlparse(value)
    return parsed.hostname


def session_region(session, fallback_region_id, region_by_host):
    for attr in ("region_id", "region"):
        value = getattr(session, attr, None)
        if value:
            return value

    for value in (getattr(session, "ws", None), getattr(session, "inspect_url", None)):
        host = host_from_url(value)
        if host and host in region_by_host:
            return region_by_host[host]

    return fallback_region_id


def print_session(index, session, region_id, region_by_host):
    print(f"Session {index}:")
    print(f"  ID: {session.id}")
    print(f"  Region: {session_region(session, region_id, region_by_host)}")
    print(f"  Status: {session.status}")
    print(f"  Browser Type: {session.browser_type}")
    print(f"  Created At: {session.created_at}")
    print(f"  Container ID: {session.container_id or 'N/A'}")
    print(f"  WebSocket URL: {session.ws or 'N/A'}")
    print(f"  Inspect URL: {session.inspect_url or 'N/A'}")
    print()


def main():
    print("=== Lexmount Session Region List ===\n")

    catalog_client = create_client()
    regions = catalog_regions(catalog_client)
    if not regions:
        regions = [{"region_id": catalog_client.region_info().get("selected_region") or "default"}]

    region_by_host = {
        region["host"]: region["region_id"]
        for region in regions
        if region.get("host") and region.get("region_id")
    }

    if region_by_host:
        print("Catalog regions:")
        for region in regions:
            print(f"  {region['region_id']}: {region.get('host', 'N/A')}")
        print()

    total_active = 0
    session_index = 1
    for region in regions:
        region_id = region["region_id"]
        client = create_client(region=region_id if region_id != "default" else None)
        result = client.sessions.list(status="active")
        total_active += len(result)

        print(f"Region {region_id}: {len(result)} active sessions")
        print(
            "  Pagination: "
            f"total={result.pagination.total_count}, "
            f"active={result.pagination.active_count}, "
            f"closed={result.pagination.closed_count}\n"
        )

        for session in result.sessions:
            print_session(session_index, session, region_id, region_by_host)
            session_index += 1

    print(f"Total active sessions across listed regions: {total_active}")
    print("=== Example Complete ===")


if __name__ == "__main__":
    main()
