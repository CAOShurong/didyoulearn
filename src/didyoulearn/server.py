"""Loopback-only static server for the browser lab."""

from __future__ import annotations

import functools
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import as_file, files
from pathlib import Path


class LocalOnlyHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; "
            "frame-ancestors 'none'; form-action 'none'",
        )
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def serve(
    directory: str | Path | None = None, *, port: int = 8765, open_browser: bool = True
) -> None:
    if not 1 <= port <= 65535:
        raise ValueError("port must be from 1 to 65535")

    def run(root: Path) -> None:
        handler = functools.partial(LocalOnlyHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", port), handler)
        url = f"http://127.0.0.1:{port}/"
        print(f"DidYouLearn local lab: {url}")
        print("Press Ctrl+C to stop.")
        if open_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()

    if directory is not None:
        run(Path(directory).resolve())
        return

    resource = files("didyoulearn").joinpath("web")
    with as_file(resource) as root:
        run(root)
