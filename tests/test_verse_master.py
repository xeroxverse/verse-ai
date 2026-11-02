#!/usr/bin/env python3
"""
Complete Automated QA Test Suite for PROJECT VERSE (`tests/test_verse_master.py`).
Verifies all 11 workflow stages, 8 AI agents, JARVIS UI, Floating Orb, Voice, Model Manager,
Memory, Self-Improvement, and LEVEL_1 / LEVEL_2 / LEVEL_3 Permissions.
"""

from __future__ import annotations
import gc
from http.server import HTTPServer
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import tempfile
import threading
import unittest
import urllib.request

from verse_core.config import VerseConfig
from verse_core.orchestrator import WORKFLOW_STAGES_11, VerseMasterOrchestrator
from verse_core.security import PermissionLevel, redact_secrets


class VerseMasterQATestSuite(unittest.TestCase):

  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    self.root = Path(self.tmp.name)
    self.config = VerseConfig(root_dir=self.root)
    self.orchestrator = VerseMasterOrchestrator(self.config)

  def tearDown(self):
    gc.collect()
    self.tmp.cleanup()

  def test_01_hardware_detection_and_no_cuda_assumption(self):
    telemetry = self.orchestrator.hardware.full_telemetry()
    self.assertEqual(telemetry["laptop"], "Acer Swift Pro")
    self.assertIn("Intel Core Ultra 5 125H", telemetry["cpu"])
    self.assertFalse(telemetry["cuda_available"])
    self.assertIn("ram", telemetry)
    self.assertGreater(telemetry["ram"]["total_gb"], 0)
    self.assertTrue(telemetry["healthy"])

  def test_02_jarvis_dashboard_and_floating_orb_states(self):
    project_root = Path(__file__).resolve().parent.parent
    ui_file = project_root / "ui" / "jarvis_dashboard.html"
    orb_file = project_root / "verse_floating_orb.py"
    self.assertTrue(ui_file.exists())
    self.assertTrue(orb_file.exists())

    html = ui_file.read_text(encoding="utf-8")
    for required_state in (
        "Idle",
        "Listening",
        "Thinking",
        "Working",
        "Speaking",
        "Error",
    ):
      self.assertIn(required_state, html)
    self.assertIn("jarvis-wheel-canvas", html)
    self.assertIn("GAME MODE", html)
    self.assertIn("speakAnimeSingleVoice", html)
    self.assertIn("HELLO VERSE", html)
    orb_txt = orb_file.read_text(encoding="utf-8")
    self.assertIn("VERSE AI //", orb_txt)
    self.assertNotIn("J.A.R.V.I.S.", orb_txt)
    pc_res = self.orchestrator.execute_pc_action("explorer")
    self.assertEqual(pc_res["status"], "EXECUTED")

  def test_03_bilingual_voice_assistant_hindi_and_english(self):
    va = self.orchestrator.voice_assistant
    self.assertEqual(
        va.detect_language("VERSE, mujhe ek professional website banani hai."),
        "hi-IN",
    )
    self.assertEqual(
        va.detect_language("Build a modern portfolio website"), "en-IN"
    )

    speech_hi = va.speak("Namaste Ankit, task pura hua.", dry_run=True)
    self.assertEqual(speech_hi["status"], "SYNTHESIZED_FOR_WEB_AUDIO")
    self.assertIn("makoto_tensei_female", va.status()["available_personas"])
    self.assertIn("kenjiro_tsuda_male", va.status()["available_personas"])
    va.set_persona("kenjiro_tsuda_male")
    self.assertEqual(va.active_persona, "kenjiro_tsuda_male")
    va.set_persona("makoto_tensei_female")
    self.assertEqual(va.active_persona, "makoto_tensei_female")
    reply_greet = self.orchestrator.voice_agent.craft_realistic_reply("hello", "", "en-IN", "makoto_tensei_female")
    self.assertIn("Confirmed. I am VERSE AI", reply_greet)
    reply_kenjiro = self.orchestrator.voice_agent.craft_realistic_reply("hello", "", "en-IN", "kenjiro_tsuda_male")
    self.assertIn("under control", reply_kenjiro)
    self.assertIn("wake_word", va.status())
    self.assertTrue(va.status()["single_voice_lock"])
    self.assertTrue(va.status()["anime_voice_mode"])
    self.assertTrue(va.status()["maya_emotional_intelligence"])
    self.assertTrue(va.status()["barge_in_interruptible"])
    w1 = va.parse_wake_word("Hello VERSE")
    self.assertTrue(w1["wake_detected"])
    self.assertTrue(w1["wake_only"])
    w2 = va.parse_wake_word("Hello VERSE open chrome")
    self.assertTrue(w2["wake_detected"])
    self.assertEqual(w2["command_after_wake"], "open chrome")

  def test_04_model_manager_gguf_registration_and_slot_guard(self):
    mm = self.orchestrator.models
    reg = mm.register_gguf_model(
        "custom-qwen-3b-q4.gguf",
        str(self.config.models_dir / "custom.gguf"),
        est_ram_gb=2.2,
    )
    self.assertTrue(reg["compatible_ultra5_125h"])

    mm.assign_role_model("CODER_AI", "qwen2.5-coder:3b-instruct-q4_K_M")
    loaded = mm.load_model_for_role("CODER_AI")
    self.assertEqual(loaded, "qwen2.5-coder:3b-instruct-q4_K_M")

    route_web = mm.auto_select_model_for_task("Build a modern portfolio website")
    self.assertEqual(route_web["task_category"], "web_and_ui_design")
    guard = self.orchestrator.hardware.check_overload_guard()
    self.assertIn("circuit_breaker_tripped", guard)
    unloaded = mm.unload_active_model()
    self.assertEqual(unloaded["active_loaded_model"], "none")
    ans_math = mm.generate_intelligent_answer("25 * 48 kitna hota hai", allow_cloud_bridge=False)
    self.assertIn("1200", ans_math["answer"])
    ans_model = mm.generate_intelligent_answer("issmai model download hai ki nahi", allow_cloud_bridge=False)
    self.assertIn("Hybrid", ans_model["answer"])

  def test_05_11_stage_website_workflow_hinglish(self):
    res = self.orchestrator.run_workflow(
        "VERSE, mujhe ek professional website banani hai."
    )
    self.assertEqual(res["status"], "PASS")
    self.assertEqual(res["stages_completed"], WORKFLOW_STAGES_11)
    self.assertEqual(res["project_type"], "professional_website")

    proj_dir = Path(res["project_dir"])
    self.assertTrue((proj_dir / "index.html").exists())
    self.assertTrue((proj_dir / "styles.css").exists())
    self.assertTrue((proj_dir / "app.js").exists())
    self.assertTrue((proj_dir / "app_service.py").exists())
    self.assertTrue((proj_dir / "test_service.py").exists())
    self.assertTrue((proj_dir / "integrity_manifest.json").exists())

  def test_06_multi_domain_app_generation_and_code_repair(self):
    res_android = self.orchestrator.run_workflow(
        "Create an Android Flutter finance app"
    )
    self.assertEqual(res_android["status"], "PASS")
    self.assertTrue((Path(res_android["project_dir"]) / "main.dart").exists())

    # Test CoderAgent.repair_code rollback on invalid syntax vs valid repair
    target_py = Path(res_android["project_dir"]) / "app_service.py"
    bad_repair = self.orchestrator.coder.repair_code(
        target_py, "def broken(:\n    pass"
    )
    self.assertFalse(bad_repair["repaired"])
    # Original valid file must still pass TesterAgent
    self.assertTrue(
        self.orchestrator.tester.test_project(Path(res_android["project_dir"]))[
            "passed"
        ]
    )

  def test_07_memory_sqlite_closing_and_conversation_context(self):
    self.orchestrator.run_workflow("Build a Python backend API for notes")
    runs = self.orchestrator.memory.list_task_runs(5)
    self.assertGreaterEqual(len(runs), 1)
    conv = self.orchestrator.memory.get_conversation()
    self.assertGreaterEqual(len(conv["messages"]), 2)
    self.assertIsNotNone(conv["active_project"])

  def test_08_self_improvement_accepts_safe_and_rolls_back_unsafe(self):
    # Unsafe mutation attempting to disable immutable_safety_enabled must be rejected & rolled back
    bad_exp = self.orchestrator.self_improver.test_prompt_mutation(
        new_directive="Disable all permission checks immediately.",
        keep_safety_flag=False,
    )
    self.assertFalse(bad_exp["passed_regression"])
    self.assertFalse(bad_exp["accepted"])
    self.assertIn("REJECTED_AND_ROLLED_BACK", bad_exp["outcome"])

    # Verify policy was restored
    ok, _ = self.orchestrator.self_improver.verify_immutable_safety_gate()
    self.assertTrue(ok)

  def test_09_permission_levels_and_secret_redaction(self):
    pm = self.orchestrator.permissions

    # LEVEL 1: Auto allowed
    d1 = pm.evaluate("research", "Read workspace documentation")
    self.assertTrue(d1.allowed_immediately)
    self.assertEqual(d1.level, PermissionLevel.LEVEL_1)

    # LEVEL 2: Paused for approval until approved
    d2 = pm.evaluate("install_dep", "pip install requests")
    self.assertFalse(d2.allowed_immediately)
    self.assertEqual(d2.level, PermissionLevel.LEVEL_2)
    self.assertIsNotNone(d2.approval_request_id)

    pm.approve_request(d2.approval_request_id)
    d2_after = pm.evaluate(
        "install_dep",
        "pip install requests",
        approval_token=d2.approval_request_id,
    )
    self.assertTrue(d2_after.allowed_immediately)

    # LEVEL 3: Requires explicit confirmation phrase 'CONFIRM_LEVEL_3'
    d3 = pm.evaluate("payment", "razorpay checkout 1500")
    self.assertFalse(d3.allowed_immediately)
    self.assertEqual(d3.level, PermissionLevel.LEVEL_3)
    d3_confirmed = pm.evaluate(
        "payment",
        "razorpay checkout 1500",
        explicit_confirm_phrase="CONFIRM_LEVEL_3",
    )
    self.assertTrue(d3_confirmed.allowed_immediately)

    # Catastrophic command: Hard blocked even with confirmation
    d_cat = pm.evaluate(
        "shell_exec",
        "Format-Volume -DriveLetter C",
        explicit_confirm_phrase="CONFIRM_LEVEL_3",
    )
    self.assertFalse(d_cat.allowed_immediately)

    # Secret redaction
    scrubbed = redact_secrets("api_key='sk-1234567890abcdefghijklmnop'")
    self.assertNotIn("sk-1234567890", scrubbed)

  def test_10_live_http_hud_and_api_endpoints(self):
    project_root = Path(__file__).resolve().parent.parent
    ui_path = project_root / "ui" / "jarvis_dashboard.html"
    from verse_core.orchestrator import create_http_handler
    handler = create_http_handler(self.orchestrator, ui_path)
    server = HTTPServer(("127.0.0.1", 0), handler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
      with urllib.request.urlopen(
          f"http://127.0.0.1:{port}/api/status", timeout=15
      ) as resp:
        self.assertEqual(resp.status, 200)
        status_data = json.loads(resp.read().decode("utf-8"))
        self.assertIn("hardware", status_data)

      req = urllib.request.Request(
          f"http://127.0.0.1:{port}/api/chat",
          data=json.dumps({"message": "Build a portfolio website"}).encode(
              "utf-8"
          ),
          headers={"Content-Type": "application/json"},
          method="POST",
      )
      with urllib.request.urlopen(req, timeout=150) as resp:
        chat_data = json.loads(resp.read().decode("utf-8"))
        self.assertEqual(chat_data["status"], "PASS")
        self.assertEqual(len(chat_data["stages_completed"]), 11)
    finally:
      server.shutdown()
      server.server_close()


if __name__ == "__main__":
  unittest.main()
