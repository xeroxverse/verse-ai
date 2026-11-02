#!/usr/bin/env python3
"""
VERSE — Master AI Orchestrator Server, CLI & Desktop Launcher (`verse.py`).
Integrates:
  - 8 Specialist AI Agents + 11-Stage Autonomous Workflow
  - JARVIS Futuristic Web HUD (`http://127.0.0.1:8765`)
  - Native Always-on-Top Floating AI Orb (`--orb`)
  - Hardware & Model Management (`--health`)
  - Automated QA Verification (`--test`)
"""

from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer as HTTPServer
import json
from pathlib import Path
import subprocess
import sys
import unittest
import webbrowser

from verse_core.config import VerseConfig
from verse_core.orchestrator import VerseMasterOrchestrator


def create_http_handler(orchestrator: VerseMasterOrchestrator, ui_html_path: Path):
  class VerseHUDHandler(BaseHTTPRequestHandler):

    def do_GET(self):
      if self.path == "/api/status":
        self._send_json(orchestrator.full_status_snapshot())
        return
      if self.path == "/api/orb-state":
        self._send_json({"orb_state": orchestrator.orb_state})
        return
      if ui_html_path.exists():
        html = ui_html_path.read_text(encoding="utf-8")
      else:
        html = "<h1>VERSE HUD Ready</h1>"
      self.send_response(200)
      self.send_header("Content-Type", "text/html; charset=utf-8")
      self.end_headers()
      self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
      length = int(self.headers.get("Content-Length", "0"))
      raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
      body = json.loads(raw or "{}")

      if self.path == "/api/chat":
        msg = body.get("message", "")
        speak = bool(body.get("speak_aloud", False))
        res = orchestrator.run_workflow(msg, speak_aloud=speak)
        self._send_json(res)
        return

      if self.path == "/api/models/assign":
        role = body.get("role", "CODER_AI")
        model = body.get("model", orchestrator.config.default_coder_model)
        res = orchestrator.models.assign_role_model(role, model)
        self._send_json({"status": "UPDATED", "role_assignments": res})
        return

      if self.path == "/api/models/unload":
        self._send_json(orchestrator.models.unload_active_model())
        return

      if self.path == "/api/permissions/approve":
        req_id = body.get("request_id", "")
        confirm = body.get("explicit_confirm_phrase")
        self._send_json(
            orchestrator.permissions.approve_request(req_id, confirm)
        )
        return

      if self.path == "/api/permissions/reject":
        req_id = body.get("request_id", "")
        self._send_json(orchestrator.permissions.reject_request(req_id))
        return

      if self.path == "/api/self-improve/test":
        ok, reason = orchestrator.self_improver.verify_immutable_safety_gate()
        self._send_json({"passed": ok, "reason": reason})
        return

      self._send_json({"status": "UNKNOWN_ENDPOINT"}, code=404)

    def _send_json(self, payload: dict, code: int = 200) -> None:
      raw = json.dumps(payload, indent=2).encode("utf-8")
      self.send_response(code)
      self.send_header("Content-Type", "application/json")
      self.end_headers()
      self.wfile.write(raw)

    def log_message(self, format, *args):
      return

  return VerseHUDHandler


def main() -> int:
  parser = argparse.ArgumentParser(
      description="VERSE — Master AI Orchestrator & JARVIS HUD"
  )
  parser.add_argument(
      "--task",
      type=str,
      help="Execute full 11-stage multi-agent workflow on a goal",
  )
  parser.add_argument(
      "--serve",
      action="store_true",
      help="Start JARVIS Futuristic HUD server on http://127.0.0.1:8765",
  )
  parser.add_argument(
      "--orb",
      action="store_true",
      help="Launch native always-on-top Floating AI Orb alongside server",
  )
  parser.add_argument(
      "--health",
      action="store_true",
      help="Print hardware, RAM, model, and security diagnostics",
  )
  parser.add_argument(
      "--test", action="store_true", help="Run complete automated QA test suite"
  )
  args = parser.parse_args()

  base_dir = Path(__file__).resolve().parent
  if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))
  if args.test:
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(base_dir / "tests"), pattern="test_*.py"
    )
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if res.wasSuccessful() else 1

  orchestrator = VerseMasterOrchestrator(VerseConfig())

  if args.health:
    print(json.dumps(orchestrator.full_status_snapshot(), indent=2))
    return 0

  if args.task:
    out = orchestrator.run_workflow(args.task)
    print(json.dumps(out, indent=2))
    return 0 if out.get("status") == "PASS" else 1

  if args.orb:
    orb_script = base_dir / "verse_floating_orb.py"
    if orb_script.exists():
      subprocess.Popen([sys.executable, str(orb_script)])

  if args.serve or args.orb:
    ui_path = base_dir / "ui" / "jarvis_dashboard.html"
    host, port = orchestrator.config.host, orchestrator.config.port
    url = f"http://{host}:{port}"
    print(f"[VERSE] JARVIS Futuristic HUD listening at {url}")
    Handler = create_http_handler(orchestrator, ui_path)
    HTTPServer((host, port), Handler).serve_forever()
    return 0

  parser.print_help()
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
