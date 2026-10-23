import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import browser_agent_recovery as recovery


class RecoveryTest(unittest.TestCase):
    def test_bound_scope_and_durable_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "job.json"
            config = dict(
                api_key="fixture-key",
                project_id="project-a",
                base_url="https://api.example.test",
            )
            calls = []

            def create(**kwargs):
                disk = json.loads(path.read_text())
                self.assertIsNone(disk["run_id"])
                self.assertEqual(
                    disk["request"],
                    {k: v for k, v in kwargs.items() if k != "idempotency_key"},
                )
                self.assertEqual(disk["idempotency_key"], kwargs["idempotency_key"])
                calls.append("create")
                return SimpleNamespace(id="run-1")

            def wait(run_id):
                self.assertEqual(run_id, "run-1")
                calls.append("wait")
                return None

            sdk = SimpleNamespace(
                browser_agent=SimpleNamespace(
                    runs=SimpleNamespace(create=create, wait=wait)
                )
            )
            with patch.dict(
                "os.environ", {"BROWSER_AGENT_JOB_FILE": str(path)}
            ), patch.object(
                recovery, "configuration", return_value=config
            ), patch.object(
                recovery, "Lexmount"
            ) as cls, patch.object(
                recovery, "report", return_value=True
            ):
                cls.return_value.__enter__.return_value = sdk
                self.assertEqual(recovery.main(), 0)
                saved = json.loads(path.read_text())
                self.assertEqual(recovery.main(), 0)
                self.assertEqual(calls, ["create", "wait", "wait"])
                for run_id in [None, "run-1"]:
                    path.write_text(json.dumps({**saved, "run_id": run_id}))
                    for key, value in [
                        ("project_id", "project-b"),
                        ("base_url", "https://other.example.test"),
                    ]:
                        old = config[key]
                        config[key] = value
                        with self.assertRaisesRegex(ValueError, "matching Project"):
                            recovery.main()
                        config[key] = old
                for changes in [
                    {"idempotency_key": None},
                    {"api_origin": None},
                    {"created_at": float("nan")},
                    {"created_at": float("inf")},
                    {"created_at": time.time() + 60},
                    {"created_at": 0},
                ]:
                    path.write_text(json.dumps({**saved, "run_id": None, **changes}))
                    with self.assertRaisesRegex(ValueError, "recovery|Recovery"):
                        recovery.main()
                self.assertEqual(calls, ["create", "wait", "wait"])


if __name__ == "__main__":
    unittest.main()
