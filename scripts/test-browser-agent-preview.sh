#!/usr/bin/env bash
set -euo pipefail
sdk_dir=$(cd "${1:?Usage: bash scripts/test-browser-agent-preview.sh /path/to/lexmount-python-sdk}" && pwd)
repo_dir=$(cd "$(dirname "$0")/.." && pwd)
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "Activate a disposable Python virtual environment before running this preview check." >&2
  exit 1
fi
cd "$repo_dir"
python -m pip install -r requirements.txt
python -m pip install "$sdk_dir"
python -c "from lexmount import Lexmount, AsyncLexmount, RunWaitTimeout; assert hasattr(Lexmount, 'browser_agent')"
python -m unittest test_quickstart_auth test_browser_agent_recovery
python -m compileall -q browser_agent.py browser_agent_async.py browser_agent_advanced.py browser_agent_common.py browser_agent_recovery.py
