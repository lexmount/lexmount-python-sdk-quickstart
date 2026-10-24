#!/usr/bin/env bash
set -euo pipefail
repo_dir=$(cd "$(dirname "$0")/.." && pwd)
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "Activate a disposable Python virtual environment before running this check." >&2
  exit 1
fi
cd "$repo_dir"
python -m pip install -r requirements.txt
python - <<'PYSDK'
import asyncio
from importlib.metadata import version
from lexmount import __version__, Lexmount, AsyncLexmount, RunWaitTimeout

assert version("lexmount") == __version__ == "0.7.0"
config = dict(api_key="package-check", project_id="package-check", base_url="https://api.example.invalid")
with Lexmount(**config) as client:
    assert callable(client.browser_agent.agents.create)
    assert callable(client.browser_agent.runs.wait)

async def check_async():
    async with AsyncLexmount(**config) as client:
        assert callable(client.browser_agent.agents.create)
        assert callable(client.browser_agent.runs.wait)

asyncio.run(check_async())
PYSDK
python -m unittest test_quickstart_auth test_browser_agent_recovery
python -m compileall -q browser_agent.py browser_agent_async.py browser_agent_advanced.py browser_agent_common.py browser_agent_recovery.py
