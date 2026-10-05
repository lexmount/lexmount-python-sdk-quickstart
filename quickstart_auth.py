"""Shared credential bootstrap for the quickstart demos (stdlib + python-dotenv)."""
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import webbrowser

from dotenv import dotenv_values
from dotenv.parser import parse_stream

DEFAULT_BASE_URL = "https://api.lexmount.com"
SITES = {
    "https://api.lexmount.com": "https://browser.lexmount.com",
    "https://api.lexmount.cn": "https://browser.lexmount.cn",
}
CREDENTIAL_KEYS = ("LEXMOUNT_PROJECT_ID", "LEXMOUNT_API_KEY", "LEXMOUNT_BASE_URL")


class SetupError(Exception):
    """A safe-to-display setup error; never includes credential material."""


def has_credential(value):
    normalized = (value or "").strip().lower().replace("-", "_")
    return bool(normalized) and not re.match(r"^(your_|replace_|<|changeme$|placeholder$)", normalized)


def can_open_browser(platform=None, env=None, interactive=None):
    platform = sys.platform if platform is None else platform
    env = os.environ if env is None else env
    interactive = sys.stdin.isatty() if interactive is None else interactive
    return (
        platform in ("darwin", "win32") and interactive
        and not any(env.get(key) for key in ("SSH_CONNECTION", "SSH_CLIENT", "SSH_TTY", "CI", "GITHUB_ACTIONS", "TF_BUILD"))
        and env.get("SESSIONNAME", "").lower() != "services"
    )


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _exchange_code(url, payload):
    request = Request(url, data=json.dumps(payload).encode("utf-8"), method="POST",
                      headers={"Content-Type": "application/json", "Accept": "application/json"})
    with build_opener(_NoRedirect).open(request, timeout=15) as response:
        raw = response.read(65537)
        if len(raw) > 65536:
            raise SetupError("Credential response is too large.")
        return json.loads(raw)


def authorize(site, base_url, *, open_browser=None, exchange=None, timeout=180):
    verifier = secrets.token_urlsafe(32)
    state = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).decode("ascii").rstrip("=")
    received = threading.Event()
    callback_lock = threading.Lock()
    result = {}
    redirect_uri = ""

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def reply(self, status, message):
            body = message.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.headers.get("Host") != urlsplit(redirect_uri).netloc or self.headers.get("Origin"):
                self.reply(403, "Invalid callback.")
                return
            try:
                parsed = urlsplit(self.path)
                query = parse_qs(parsed.query, keep_blank_values=True)
            except ValueError:
                self.reply(400, "Invalid callback.")
                return
            if parsed.path != "/callback":
                self.reply(404, "Not found.")
                return
            states = query.get("state", [])
            if len(states) != 1 or not hmac.compare_digest(states[0].encode("utf-8"), state.encode("ascii")):
                self.reply(400, "Invalid callback state.")
                return
            codes = query.get("code", [])
            if "error" not in query and (len(codes) != 1 or not re.fullmatch(r"[A-Za-z0-9._~-]{1,2048}", codes[0])):
                self.reply(400, "Invalid authorization code.")
                return
            with callback_lock:
                if received.is_set():
                    self.reply(409, "Authorization already received.")
                    return
                if "error" in query:
                    result["error"] = True
                else:
                    result["code"] = codes[0]
                received.set()
            if "error" in query:
                self.reply(400, "Authorization cancelled. Return to the terminal.")
            else:
                self.reply(200, "Authorization received. Return to the terminal to finish setup.")

        def log_message(self, *_args):
            pass  # Callback URLs contain one-time secrets and must never be logged.

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    redirect_uri = f"http://127.0.0.1:{server.server_port}/callback"
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    try:
        query = urlencode({
            "source": "sdk-quickstart", "intent": "agent-browser-control", "response": "code",
            "client_name": "Lexmount Python Quickstart", "scope": "browser:actions browser:sessions browser:contexts",
            "redirect_uri": redirect_uri, "state": state, "code_challenge": challenge, "code_challenge_method": "S256",
        })
        if not (open_browser or webbrowser.open)(f"{site}/connect/codex?{query}"):
            raise SetupError("Unable to open a local browser.")
        if not received.wait(timeout):
            raise SetupError("Authorization timed out.")
        if result.get("error"):
            raise SetupError("Authorization was cancelled.")
        credentials = (exchange or _exchange_code)(f"{site}/api/connect/codex/exchange", {
            "code": result["code"], "code_verifier": verifier, "redirect_uri": redirect_uri,
        })
        if not isinstance(credentials, dict) or credentials.get("ok") is not True or not all(
            isinstance(credentials.get(key), str) and has_credential(credentials[key])
            and re.fullmatch(r"[A-Za-z0-9._~+/:=-]{1,4096}", credentials[key])
            for key in ("project_id", "api_key")
        ):
            raise SetupError("Credential exchange did not return a valid project and API key.")
        if not isinstance(credentials.get("api_base_url"), str) or credentials["api_base_url"].rstrip("/") != base_url:
            raise SetupError("Authorization returned a different API environment.")
        return credentials
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


def _read_env(file):
    try:
        with file.open(encoding="utf-8", newline="") as source:
            return source.read()
    except FileNotFoundError:
        return ""


def save_credentials(file, original, credentials):
    values = {
        "LEXMOUNT_PROJECT_ID": credentials["project_id"],
        "LEXMOUNT_API_KEY": credentials["api_key"],
        "LEXMOUNT_BASE_URL": credentials["api_base_url"].rstrip("/"),
    }
    newline = "\r\n" if "\r\n" in original else "\n"
    chunks = []
    seen = set()
    # Parse complete bindings, including multiline values; preserve unrelated settings/comments.
    for binding in parse_stream(StringIO(original)):
        if binding.key in values:
            leading = re.match(r"\s*", binding.original.string).group(0)
            chunks.append(f"{leading}{binding.key}={values[binding.key]}{newline}")
            seen.add(binding.key)
        else:
            chunks.append(binding.original.string)
    updated = "".join(chunks)
    if updated and not updated.endswith("\n"):
        updated += newline
    for key in CREDENTIAL_KEYS:
        if key not in seen:
            updated += f"{key}={values[key]}{newline}"
    if file.is_symlink() or (file.exists() and not file.is_file()):
        raise SetupError("The .env path must be a regular file.")
    if _read_env(file) != original:
        raise SetupError("The .env file changed during login. Please retry.")
    descriptor, temporary = tempfile.mkstemp(prefix=file.name + ".", suffix=".tmp", dir=file.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as target:
            target.write(updated)
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, file)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_environment():
    """Load only the current directory's .env; importing a demo never opens a browser."""
    values = dotenv_values(stream=StringIO(_read_env(Path.cwd() / ".env")))
    os.environ.update({key: value for key, value in values.items() if value is not None})
    os.environ["LEXMOUNT_BASE_URL"] = os.environ.get("LEXMOUNT_BASE_URL", "").strip() or DEFAULT_BASE_URL


def ensure_credentials(*, env_file=None, env=None, browser_available=None, login=None):
    env = os.environ if env is None else env
    file = Path(os.path.abspath(env_file or ".env"))
    original = _read_env(file)
    # Preserve previous demo precedence: .env overrides exported variables.
    env.update({key: value for key, value in dotenv_values(stream=StringIO(original)).items() if value is not None})
    base_url = (env.get("LEXMOUNT_BASE_URL", "").strip() or DEFAULT_BASE_URL).rstrip("/")
    env["LEXMOUNT_BASE_URL"] = base_url
    if has_credential(env.get("LEXMOUNT_PROJECT_ID")) and has_credential(env.get("LEXMOUNT_API_KEY")):
        return
    site = SITES.get(base_url)
    manual = (
        f"Open {site or 'https://browser.lexmount.com'} and obtain the Project ID and API key for your API environment.\n"
        f"Set LEXMOUNT_PROJECT_ID and LEXMOUNT_API_KEY in {file}, then rerun this demo.\n"
        "Custom API environments require credentials from their matching website."
    )
    if not site or not (browser_available or (lambda: can_open_browser(env=env)))():
        raise SetupError(f"Lexmount credentials are missing or still contain example values.\n{manual}")
    print("Lexmount credentials are missing. Opening your browser to sign in and authorize (up to 3 minutes).")
    try:
        credentials = (login or authorize)(site, base_url)
        save_credentials(file, original, credentials)
        env.update({"LEXMOUNT_PROJECT_ID": credentials["project_id"], "LEXMOUNT_API_KEY": credentials["api_key"],
                    "LEXMOUNT_BASE_URL": credentials["api_base_url"].rstrip("/")})
    except (Exception, KeyboardInterrupt):
        # Do not include raw HTTP errors, callback URLs, API keys or server responses.
        raise SetupError(f"Browser authorization or saving .env failed. No demo requests were started.\n{manual}") from None
    print("Lexmount credentials saved to .env. Continuing the demo.")


def prepare_demo():
    """CLI wrapper with a clean, nonzero failure and no credential-bearing traceback."""
    try:
        ensure_credentials()
    except SetupError as error:
        raise SystemExit(str(error)) from None
