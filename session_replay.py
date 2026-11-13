"""Query one existing session's replay without creating or closing a browser."""
import argparse
import json
import os
import sys

from lexmount import Lexmount
from quickstart_auth import ensure_credentials


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session-id', required=True, help='Existing recorded session ID')
    parser.add_argument('--tab-id', help='Optional recorded tab ID')
    args = parser.parse_args(argv)
    if not args.session_id.strip() or (args.tab_id is not None and not args.tab_id.strip()):
        parser.error('Session ID and optional tab ID must not be empty.')
    ensure_credentials()
    with Lexmount(
        api_key=os.environ['LEXMOUNT_API_KEY'],
        project_id=os.environ['LEXMOUNT_PROJECT_ID'],
        base_url=os.getenv('LEXMOUNT_BASE_URL', 'https://api.lexmount.com'),
    ) as client:
        replay = client.sessions.get_replay(args.session_id)
        url = replay.replay_url
        if args.tab_id is not None:
            tab = next((item for item in replay.tabs if item.tab_id == args.tab_id), None)
            if tab is None:
                raise ValueError('Requested tab is not present in the replay response.')
            url = tab.replay_url
        print(json.dumps({
            'session_id': replay.session_id,
            'replay_status': replay.replay_status,
            'replay_url': url,
            'tabs': [{'tab_id': tab.tab_id, 'replay_url': tab.replay_url} for tab in replay.tabs],
        }, indent=2))
        # For just the URL, use client.sessions.get_replay_url(session_id, tab_id=tab_id).
        # A null URL is normal until the recording has completed processing.


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Never dump request objects/headers, which can contain API keys.
        if hasattr(error, 'status_code'):
            print('Replay request failed:', error.status_code,
                  getattr(error, 'code', None), getattr(error, 'request_id', None), file=sys.stderr)
        else:
            print(str(error), file=sys.stderr)
        sys.exit(1)
