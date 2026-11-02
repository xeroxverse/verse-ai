#!/usr/bin/env python3
"""
VERSE AI v14.0 — Master AI Orchestrator Server, CLI & Desktop Launcher (`verse.py`).
Integrates:
  - 8 Specialist AI Agents + 11-Stage Autonomous Workflow
  - Hyper-Animated 5-Canvas 60-FPS SHIELD OS Web HUD (`http://127.0.0.1:8765`)
  - Native Always-on-Top Floating AI Orb (`--orb`)
  - Expressive Anime/Natural Voice + Emotion Detection + Barge-In (`verse_core/voice.py`)
  - Autonomous Task-to-Model Brain Router & 80% RAM Overload Circuit Breaker
  - Automated QA Verification (`--test`)
"""

from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
import webbrowser

from verse_core.config import VerseConfig
from verse_core.orchestrator import VerseMasterOrchestrator


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def create_http_handler(orchestrator: VerseMasterOrchestrator, ui_html_path: Path):
    class VerseHUDHandler(BaseHTTPRequestHandler):

        def _send_no_cache_headers(self) -> None:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")

        def do_GET(self):
            if self.path.startswith("/api/status"):
                self._send_json(orchestrator.full_status_snapshot())
                return
            if self.path.startswith("/api/orb-state"):
                self._send_json({"orb_state": orchestrator.orb_state})
                return
            if ui_html_path.exists():
                html = ui_html_path.read_text(encoding="utf-8")
            else:
                html = "<h1>VERSE AI v14.0 SHIELD OS HUD Ready</h1>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self._send_no_cache_headers()
            self.end_headers()
            try:
                self.wfile.write(html.encode("utf-8"))
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                pass

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            body = json.loads(raw or "{}")

            if self.path == "/api/chat":
                msg = body.get("message", "")
                res = orchestrator.run_workflow(msg, speak_aloud=False)
                self._send_json(res)
                return

            if self.path == "/api/tts":
                text = body.get("text", "")
                persona = body.get("persona", orchestrator.voice_assistant.active_persona)
                lang = body.get("language")
                self._send_json(orchestrator.voice_assistant.synthesize_neural_mp3_base64(text, persona=persona, language=lang))
                return

            if self.path == "/api/voice/persona":
                persona = body.get("persona", "makoto_tensei_female")
                self._send_json(orchestrator.voice_assistant.set_persona(persona))
                return

            if self.path == "/api/voice/stop":
                self._send_json(orchestrator.voice_assistant.stop_speaking())
                return
            if self.path == "/api/pc/action":
                act = body.get("action", "")
                self._send_json(orchestrator.execute_pc_action(act))
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
            if self.path == "/api/models/pull":
                tag = body.get("model", "qwen2.5:1.5b")
                self._send_json(orchestrator.models.pull_local_ollama_model(tag))
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
            self._send_no_cache_headers()
            self.end_headers()
            try:
                self.wfile.write(raw)
            except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, format, *args):
            return

    return VerseHUDHandler


def main() -> int:
    parser = argparse.ArgumentParser(
        description="VERSE AI v14.0 — Master AI Orchestrator & Hyper-Animated SHIELD OS HUD"
    )
    parser.add_argument(
        "--task",
        type=str,
        help="Execute full 11-stage multi-agent workflow on a goal",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start SHIELD OS Futuristic HUD server on http://127.0.0.1:8765",
    )
    parser.add_argument(
        "--orb",
        action="store_true",
        help="Launch native always-on-top Floating AI Orb alongside server",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not auto-open browser when starting server",
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
        import unittest
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

    # Floating desktop orb popup removed per user request (clean single-window HUD mode)
    if False and args.orb:
        pass

    # If no flags are provided, or if --serve / --orb / --chat are provided: run Live Dual-Mode!
    ui_path = base_dir / "ui" / "jarvis_dashboard.html"
    host, port = orchestrator.config.host, orchestrator.config.port
    cache_bust_url = f"http://{host}:{port}/?v=shield_v20_{int(time.time())}"
    print("======================================================================")
    print("   VERSE AI v20.0 ULTRA — Live Dual-Mode (Web HUD + PowerShell CLI)   ")
    print(f"   Web HUD   : {cache_bust_url}")
    print("   Terminal  : Type any question, code request, or 'exit' below")
    print("======================================================================")

    orchestrator.models.ensure_ollama_daemon_running()
    orchestrator.voice_assistant.prewarm_common_phrases_async()
    Handler = create_http_handler(orchestrator, ui_path)
    httpd = ReusableThreadingHTTPServer((host, port), Handler)

    # Start HTTP HUD in background daemon thread
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(cache_bust_url)).start()

    # Interactive Terminal Loop on the main thread (Terminal & Web HUD both work simultaneously!)
    # In non-interactive/headless environments, serve_forever cleanly
    if not sys.stdin.isatty():
        try:
            while server_thread.is_alive():
                time.sleep(1.0)
        except (KeyboardInterrupt, SystemExit):
            pass
        return 0

    while True:
        try:
            user_in = input("\nYou (Ankit): ").strip()
            if not user_in:
                continue
            if user_in.lower() in {"exit", "quit", "q", "stop"}:
                print("VERSE AI: Goodbye Commander Ankit. All subsystems safe.")
                break
            res = orchestrator.run_workflow(user_in, speak_aloud=True)
            reply = (
                res.get("ai_answer")
                or res.get("voice_report", {}).get("spoken_text")
                or res.get("ceo_review", {}).get("ceo_summary")
                or "Confirmed."
            )
            print(f"\nVERSE AI: {reply}")
        except (KeyboardInterrupt, EOFError):
            print("\n[VERSE AI] Shutting down cleanly.")
            break

    httpd.shutdown()
    httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
