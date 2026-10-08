import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

from dotenv import dotenv_values
import quickstart_auth as auth

SITE = 'https://browser.lexmount.com'
CREDENTIALS = dict(ok=True, project_id='project-test', api_key='api-test-only', api_base_url=auth.DEFAULT_BASE_URL)


def request_status(url, headers=None):
    try:
        with urlopen(Request(url, headers=headers or {}), timeout=2) as response:
            return response.status
    except HTTPError as error:
        return error.code


def callback_url(raw, code='good'):
    params = parse_qs(urlsplit(raw).query)
    return f"{params['redirect_uri'][0]}?state={params['state'][0]}&code={code}"


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / '.env'

    def test_existing_env_and_default(self):
        self.file.write_text('LEXMOUNT_PROJECT_ID=from-file\nLEXMOUNT_API_KEY=file-key\n')
        env = dict(LEXMOUNT_PROJECT_ID='from-shell', LEXMOUNT_API_KEY='shell-key')
        auth.ensure_credentials(env_file=self.file, env=env, browser_available=lambda: self.fail('Unexpected browser'))
        self.assertEqual(env['LEXMOUNT_PROJECT_ID'], 'from-file')
        self.assertEqual(env['LEXMOUNT_API_KEY'], 'file-key')
        self.assertEqual(env['LEXMOUNT_BASE_URL'], auth.DEFAULT_BASE_URL)

    def test_missing_partial_and_placeholder_headless(self):
        for content in ('', 'LEXMOUNT_PROJECT_ID=present\n',
                        'LEXMOUNT_PROJECT_ID=your_project_id_here\nLEXMOUNT_API_KEY=your-api-key-here\n'):
            with self.subTest(content=content):
                self.file.write_text(content)
                with self.assertRaisesRegex(auth.SetupError, r'https://browser.lexmount.com'):
                    auth.ensure_credentials(env_file=self.file, env={}, browser_available=lambda: False,
                                            login=lambda *_: self.fail('Unexpected login'))
                self.assertEqual(self.file.read_text(), content)

    def test_platform_detection(self):
        for platform in ('darwin', 'win32'):
            self.assertTrue(auth.can_open_browser(platform, {}, True))
            self.assertFalse(auth.can_open_browser(platform, {}, False))
            for key in ('SSH_CONNECTION', 'SSH_CLIENT', 'SSH_TTY', 'CI', 'GITHUB_ACTIONS', 'TF_BUILD'):
                self.assertFalse(auth.can_open_browser(platform, {key: '1'}, True))
        self.assertFalse(auth.can_open_browser('linux', {}, True))
        self.assertFalse(auth.can_open_browser('win32', {'SESSIONNAME': 'Services'}, True))

    def test_pkce_real_loopback_callback(self):
        captured = {}

        def open_browser(raw):
            url = urlsplit(raw)
            self.assertEqual(url.scheme + '://' + url.netloc, SITE)
            self.assertEqual(url.path, '/connect/codex')
            params = parse_qs(url.query)
            captured.update(params)
            self.assertEqual(params['code_challenge_method'], ['S256'])
            redirect = params['redirect_uri'][0]
            self.assertEqual(urlsplit(redirect).hostname, '127.0.0.1')
            self.assertEqual(request_status(redirect.replace('/callback', '/favicon.ico')), 404)
            self.assertEqual(request_status(redirect + '?state=forged&code=bad'), 400)
            self.assertEqual(request_status(callback_url(raw), {'Origin': 'https://foreign.example'}), 403)
            self.assertEqual(request_status(callback_url(raw), {'Host': 'foreign.example'}), 403)
            self.assertEqual(request_status(callback_url(raw) + '&state=duplicate'), 400)
            self.assertEqual(request_status(callback_url(raw)), 200)
            self.assertEqual(request_status(callback_url(raw, 'second')), 409)
            return True

        def exchange(url, payload):
            self.assertEqual(url, SITE + '/api/connect/codex/exchange')
            self.assertEqual(payload['code'], 'good')
            self.assertEqual(payload['redirect_uri'], captured['redirect_uri'][0])
            self.assertRegex(payload['code_verifier'], r'^[A-Za-z0-9_-]{43}$')
            challenge = base64.urlsafe_b64encode(hashlib.sha256(payload['code_verifier'].encode()).digest()).decode().rstrip('=')
            self.assertEqual(challenge, captured['code_challenge'][0])
            return CREDENTIALS

        self.assertEqual(auth.authorize(SITE, auth.DEFAULT_BASE_URL, open_browser=open_browser, exchange=exchange), CREDENTIALS)
        with self.assertRaises(URLError):
            urlopen(captured['redirect_uri'][0], timeout=1)

    def test_browser_failure_cancel_and_timeout(self):
        def exchange(*_):
            self.fail('Unexpected exchange')
        with self.assertRaisesRegex(auth.SetupError, 'local browser'):
            auth.authorize(SITE, auth.DEFAULT_BASE_URL, open_browser=lambda _: False, exchange=exchange)
        def cancel(raw):
            request_status(callback_url(raw).replace('code=good', 'error=access_denied'))
            return True
        with self.assertRaisesRegex(auth.SetupError, 'cancelled'):
            auth.authorize(SITE, auth.DEFAULT_BASE_URL, open_browser=cancel, exchange=exchange)
        def forge(raw):
            params = parse_qs(urlsplit(raw).query)
            request_status(params['redirect_uri'][0] + '?state=forged&code=bad')
            return True
        with self.assertRaisesRegex(auth.SetupError, 'timed out'):
            auth.authorize(SITE, auth.DEFAULT_BASE_URL, open_browser=forge, exchange=exchange, timeout=0.03)

    def test_invalid_exchange_responses(self):
        for response in (None, dict(CREDENTIALS, ok=False), dict(CREDENTIALS, api_key=''),
                         dict(CREDENTIALS, project_id='bad\nINJECT=1'), dict(CREDENTIALS, api_base_url=None),
                         dict(CREDENTIALS, api_base_url='https://api.lexmount.cn')):
            with self.subTest(response=response):
                with self.assertRaises(auth.SetupError):
                    auth.authorize(SITE, auth.DEFAULT_BASE_URL,
                                   open_browser=lambda raw: request_status(callback_url(raw)) == 200,
                                   exchange=lambda *_: response)

    def test_real_http_exchange(self):
        captured = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                captured.append((self.path, json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
                data = json.dumps(CREDENTIALS).encode()
                self.send_response(200)
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            def log_message(self, *_):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = auth.authorize(f'http://127.0.0.1:{server.server_port}', auth.DEFAULT_BASE_URL,
                                    open_browser=lambda raw: request_status(callback_url(raw)) == 200)
            self.assertEqual(result, CREDENTIALS)
            self.assertEqual(captured[0][0], '/api/connect/codex/exchange')
            self.assertEqual(captured[0][1]['code'], 'good')
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_save_pair_preserving_multiline_and_permissions(self):
        original = ('# custom settings\r\nMULTI="hello\r\nLEXMOUNT_API_KEY=not-an-assignment\r\nworld"\r\n'
                    'export LEXMOUNT_PROJECT_ID=old-project\r\nLEXMOUNT_API_KEY=your_api_key_here\r\nOTHER="value # keep"\r\n')
        self.file.write_bytes(original.encode())
        env = {}
        auth.ensure_credentials(env_file=self.file, env=env, browser_available=lambda: True, login=lambda *_: CREDENTIALS)
        saved = self.file.read_bytes().decode()
        parsed = dotenv_values(stream=StringIO(saved))
        self.assertEqual(parsed['MULTI'], dotenv_values(stream=StringIO(original))['MULTI'])
        self.assertEqual(parsed['OTHER'], 'value # keep')
        self.assertEqual(parsed['LEXMOUNT_PROJECT_ID'], CREDENTIALS['project_id'])
        self.assertEqual(parsed['LEXMOUNT_API_KEY'], CREDENTIALS['api_key'])
        self.assertEqual(env['LEXMOUNT_API_KEY'], CREDENTIALS['api_key'])
        self.assertNotIn('old-project', saved)
        if os.name != 'nt':
            self.assertEqual(self.file.stat().st_mode & 0o777, 0o600)

    def test_concurrent_edits_and_failure_do_not_overwrite(self):
        self.file.write_text('# changed\n')
        with self.assertRaisesRegex(auth.SetupError, 'changed during login'):
            auth.save_credentials(self.file, '# before\n', CREDENTIALS)
        env = dict(LEXMOUNT_PROJECT_ID='partial')
        def fail(*_):
            raise RuntimeError('sensitive-response-MUST-NOT-LEAK')
        with self.assertRaises(auth.SetupError) as error:
            auth.ensure_credentials(env_file=self.file, env=env, browser_available=lambda: True, login=fail)
        self.assertNotIn('sensitive-response', str(error.exception))
        self.assertEqual(self.file.read_text(), '# changed\n')
        self.assertEqual(env['LEXMOUNT_PROJECT_ID'], 'partial')

    def test_cn_and_custom_environment(self):
        def login(site, base):
            self.assertEqual(site, 'https://browser.lexmount.cn')
            return dict(CREDENTIALS, api_base_url=base)
        auth.ensure_credentials(env_file=self.file, env=dict(LEXMOUNT_BASE_URL='https://api.lexmount.cn'),
                                browser_available=lambda: True, login=login)
        self.file.unlink()
        with self.assertRaisesRegex(auth.SetupError, 'matching website'):
            auth.ensure_credentials(env_file=self.file, env=dict(LEXMOUNT_BASE_URL='https://private.example'),
                                    browser_available=lambda: True, login=lambda *_: self.fail('Unexpected login'))

    def test_every_demo_stops_before_network_when_headless(self):
        repo = Path(__file__).parent
        demos = [file for file in repo.glob('*.py') if file.name not in ('quickstart_auth.py', Path(__file__).name)]
        self.assertEqual(len(demos), 20)
        env = {key: value for key, value in os.environ.items() if not key.startswith('LEXMOUNT_')}
        env['CI'] = '1'
        for demo in demos:
            with self.subTest(demo=demo.name):
                args = ['source-context'] if demo.name == 'context_fork.py' else []
                if demo.name == 'custom_image_demo.py':
                    args = ['--custom_image_id', 'test-image']
                # Fail on any unexpected network access, even if an entry point missed bootstrap.
                runner = ('import runpy,sys; from unittest.mock import patch; '
                          'sys.path.insert(0, sys.argv[1]); del sys.argv[1]; '
                          'guard=patch("socket.socket.connect", side_effect=AssertionError("unexpected network")); '
                          'guard.start(); script=sys.argv.pop(1); runpy.run_path(script, run_name="__main__")')
                result = subprocess.run([sys.executable, '-c', runner, str(repo), str(demo), *args],
                                        cwd=self.temp.name, env=env, input='', capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Lexmount credentials are missing', result.stderr)
                self.assertNotIn('unexpected network', result.stderr)


if __name__ == '__main__':
    unittest.main()
