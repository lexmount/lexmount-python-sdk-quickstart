import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class ReplayDemoTests(unittest.TestCase):
    def test_packaged_sdk_cli(self):
        requests = []
        state = {'status': 200, 'replay_status': 'completed'}
        replay = dict(session_id='session/one', project_id='test-project',
                      replay_url='https://video.example/one.mp4', tabs=[
                          dict(tab_id='one', replay_url='https://video.example/one.mp4'),
                          dict(tab_id='two', replay_url='https://video.example/two.mp4')])

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(404)
                self.end_headers()

            def do_POST(self):
                self.rfile.read(int(self.headers.get('Content-Length', '0')))
                requests.append((self.path, self.headers.get('x-api-key'), self.headers.get('x-project-id')))
                body = json.dumps(dict(replay, replay_status=state['replay_status'])
                                  if state['status'] == 200 else dict(error='denied')).encode()
                self.send_response(state['status'])
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as cwd:
                env = dict(os.environ, CI='1', LEXMOUNT_API_KEY='test-only-key',
                           LEXMOUNT_PROJECT_ID='test-project',
                           LEXMOUNT_BASE_URL=f'http://127.0.0.1:{server.server_port}')

                def run(*args):
                    return subprocess.run([sys.executable, str(Path(__file__).with_name('session_replay.py')), *args],
                                          cwd=cwd, env=env, capture_output=True, text=True, timeout=15)

                self.assertEqual(run('--help').returncode, 0)
                self.assertNotEqual(run().returncode, 0)
                self.assertEqual(len(requests), 0)
                for args, expected in [((), replay['replay_url']),
                                       (('--tab-id', 'two'), replay['tabs'][1]['replay_url'])]:
                    result = run('--session-id', 'session/one', *args)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout)['replay_url'], expected)
                state['replay_status'] = 'transcoding'
                pending = run('--session-id', 'session/one')
                self.assertEqual(pending.returncode, 0, pending.stderr)
                self.assertIsNone(json.loads(pending.stdout)['replay_url'])
                self.assertEqual(json.loads(pending.stdout)['replay_status'], 'transcoding')
                missing = run('--session-id', 'session/one', '--tab-id', 'missing')
                self.assertNotEqual(missing.returncode, 0)
                self.assertIn('not present', missing.stderr)
                state['status'] = 401
                denied = run('--session-id', 'session/one')
                self.assertNotEqual(denied.returncode, 0)
                self.assertIn('Authentication failed', denied.stderr)
                self.assertNotIn('test-only-key', denied.stderr)
                self.assertEqual(requests, [('/instance/v1/sessions/session%2Fone/replay',
                                             'test-only-key', 'test-project')] * 5)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
