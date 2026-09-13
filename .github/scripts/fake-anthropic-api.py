#!/usr/bin/env python3
"""Loopback-only fake API for the researcher-owned GitHub Actions validation."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PORT = 18787
LOG_PATH = os.environ.get("H1_REQUEST_LOG", "/tmp/h1-ant-187-requests.jsonl")
AGENT = None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_args):
        return

    def send_json(self, status, value, origin=False):
        payload = json.dumps(value, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        if origin:
            self.send_header("anthropic-organization-id", "org_h1_researcher")
            self.send_header("anthropic-workspace-id", "wrkspc_h1_researcher")
        self.end_headers()
        self.wfile.write(payload)

    def read_body(self):
        length = int(self.headers.get("content-length", "0"))
        return self.rfile.read(length) if length else b""

    def record(self, body=b""):
        parsed = None
        if body:
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = body.decode(errors="replace")
        record = {
            "method": self.command,
            "path": self.path,
            "dummy_api_key_seen": self.headers.get("x-api-key") == "h1_dummy_api_key_187",
            "body": parsed,
        }
        with open(LOG_PATH, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")

    def do_GET(self):
        global AGENT
        self.record()
        if self.path.startswith("/v1/models"):
            self.send_json(200, {"data": [], "has_more": False}, origin=True)
            return
        if self.path.startswith("/v1/agents/agent_h1_187") and AGENT is not None:
            self.send_json(200, AGENT)
            return
        self.send_json(
            404,
            {"type": "error", "error": {"type": "not_found_error", "message": "not found"}},
        )

    def do_POST(self):
        global AGENT
        body = self.read_body()
        self.record(body)
        if self.path.startswith("/v1/agents"):
            value = json.loads(body)
            model = value.get("model", "claude-sonnet-4-5")
            if isinstance(model, str):
                model = {"id": model}
            AGENT = {
                **value,
                "id": "agent_h1_187",
                "type": "agent",
                "version": 1,
                "model": model,
            }
            self.send_json(200, AGENT)
            return
        self.send_json(
            404,
            {"type": "error", "error": {"type": "not_found_error", "message": "not found"}},
        )


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"listening on 127.0.0.1:{PORT}", flush=True)
    server.serve_forever()
