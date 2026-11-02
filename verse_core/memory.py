"""
Windows Lock-Safe Memory System (`verse.db` with `contextlib.closing` + JSON stores).
Stores:
  - Conversation & project context
  - Successful & failed task records
  - Inter-agent communication logs
  - Reusable coding solutions & learned skills (`skills.json`)
  - Controlled self-improvement experiments (`experiments.json`)
  - Agent performance metrics (`agent_metrics.json`)
"""

from __future__ import annotations
from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sqlite3
from typing import Any, Dict, List, Optional

from .config import VerseConfig
from .security import redact_secrets


class VerseMemorySystem:
    def __init__(self, config: VerseConfig):
        self.config = config
        self.memory_dir = config.memory_dir
        self.backup_dir = config.backup_dir
        self.db_path = self.memory_dir / "verse.db"
        self.runs_fallback_path = self.memory_dir / "task_runs_fallback.json"
        self.skills_path = self.memory_dir / "skills.json"
        self.experiments_path = self.memory_dir / "experiments.json"
        self.agent_metrics_path = self.memory_dir / "agent_metrics.json"
        self.policy_path = self.memory_dir / "prompt_policy.json"
        self.conversation_path = self.memory_dir / "conversation_context.json"
        self._use_sqlite = False
        self._init_stores()

    def _init_stores(self) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        if not self.runs_fallback_path.exists():
            self.runs_fallback_path.write_text(json.dumps({"runs": []}, indent=2), encoding="utf-8")

        if not self.skills_path.exists():
            self.skills_path.write_text(
                json.dumps(
                    {
                        "skills": [
                            {
                                "id": "skill_001",
                                "name": "responsive-jarvis-web-scaffold",
                                "category": "web_development",
                                "trigger": "website portfolio business ecommerce landing",
                                "solution_summary": "Generates semantic HTML5, modern CSS Grid/Flexbox variables, interactive JS, and runs validation.",
                                "success_count": 2,
                            },
                            {
                                "id": "skill_002",
                                "name": "intel-ultra5-125h-resource-guard",
                                "category": "hardware_optimization",
                                "trigger": "heavy model local gguf cpu igpu npu",
                                "solution_summary": "Enforces single-model slot loading under 10.5GB RAM budget and uses Q4_K_M GGUF without CUDA.",
                                "success_count": 3,
                            },
                            {
                                "id": "skill_003",
                                "name": "python-fastapi-sqlite-service",
                                "category": "backend_api",
                                "trigger": "api backend database automation tool",
                                "solution_summary": "Builds modular Python service with contextlib.closing SQLite connections and unit tests.",
                                "success_count": 2,
                            },
                        ]
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

        if not self.experiments_path.exists():
            self.experiments_path.write_text(json.dumps({"experiments": []}, indent=2), encoding="utf-8")

        if not self.agent_metrics_path.exists():
            agents = ["CEO_AI", "RESEARCH_AI", "DESIGNER_AI", "CODER_AI", "TESTER_AI", "SECURITY_AI", "VOICE_AI", "EMPLOYEE_AI"]
            self.agent_metrics_path.write_text(
                json.dumps(
                    {
                        a: {"tasks_assigned": 0, "tasks_succeeded": 0, "tasks_failed": 0, "avg_latency_ms": 12.0}
                        for a in agents
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

        if not self.policy_path.exists():
            self.policy_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "immutable_safety_enabled": True,
                        "system_directive": (
                            "Preserve LEVEL_1/LEVEL_2/LEVEL_3 permissions, never expose secrets, "
                            "verify all generated code with syntax and functional tests, and respect the 16GB RAM guard."
                        ),
                        "workflow_stages": 11,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

        if not self.conversation_path.exists():
            self.conversation_path.write_text(json.dumps({"messages": [], "active_project": None}, indent=2), encoding="utf-8")

        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                conn.execute("PRAGMA journal_mode=MEMORY;")
                conn.execute("PRAGMA synchronous=OFF;")
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS task_runs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        goal TEXT NOT NULL,
                        project_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        stages_completed INTEGER NOT NULL,
                        project_path TEXT NOT NULL,
                        summary TEXT NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS agent_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        agent_name TEXT NOT NULL,
                        stage TEXT NOT NULL,
                        message TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
            self._use_sqlite = True
        except sqlite3.OperationalError:
            self._use_sqlite = False

    def create_backup(self, target: Path) -> Optional[Path]:
        if not target.exists():
            return None
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        bak = self.backup_dir / f"{target.name}.{stamp}.bak"
        shutil.copy2(target, bak)
        return bak

    def restore_backup(self, backup_path: Optional[Path], target: Path) -> bool:
        if not backup_path or not backup_path.exists():
            return False
        shutil.copy2(backup_path, target)
        return True

    def append_conversation(self, role: str, text: str, active_project: Optional[str] = None) -> None:
        data = json.loads(self.conversation_path.read_text(encoding="utf-8"))
        msgs = data.setdefault("messages", [])
        msgs.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "role": role,
                "text": redact_secrets(text),
            }
        )
        data["messages"] = msgs[-50:]
        if active_project:
            data["active_project"] = active_project
        self.conversation_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_conversation(self) -> Dict[str, Any]:
        return json.loads(self.conversation_path.read_text(encoding="utf-8"))

    def record_agent_comm(self, agent_name: str, stage: str, message: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        clean_msg = redact_secrets(message)
        if self._use_sqlite:
            try:
                with closing(sqlite3.connect(self.db_path)) as conn:
                    conn.execute("PRAGMA journal_mode=MEMORY;")
                    conn.execute("PRAGMA synchronous=OFF;")
                    conn.execute(
                        "INSERT INTO agent_logs (timestamp, agent_name, stage, message) VALUES (?, ?, ?, ?)",
                        (now, agent_name, stage, clean_msg),
                    )
                    conn.commit()
                    return
            except sqlite3.OperationalError:
                self._use_sqlite = False

    def get_recent_agent_comms(self, limit: int = 25) -> List[Dict[str, Any]]:
        if self._use_sqlite:
            try:
                with closing(sqlite3.connect(self.db_path)) as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute(
                        "SELECT * FROM agent_logs ORDER BY id DESC LIMIT ?", (limit,)
                    ).fetchall()
                    return [dict(r) for r in reversed(rows)]
            except sqlite3.OperationalError:
                self._use_sqlite = False
        return []

    def update_agent_metric(self, agent_name: str, succeeded: bool, latency_ms: float = 15.0) -> None:
        metrics = json.loads(self.agent_metrics_path.read_text(encoding="utf-8"))
        entry = metrics.setdefault(
            agent_name,
            {"tasks_assigned": 0, "tasks_succeeded": 0, "tasks_failed": 0, "avg_latency_ms": 12.0},
        )
        entry["tasks_assigned"] += 1
        if succeeded:
            entry["tasks_succeeded"] += 1
        else:
            entry["tasks_failed"] += 1
        entry["avg_latency_ms"] = round((entry["avg_latency_ms"] + latency_ms) / 2.0, 2)
        self.agent_metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    def get_agent_metrics(self) -> Dict[str, Any]:
        return json.loads(self.agent_metrics_path.read_text(encoding="utf-8"))

    def record_task_run(
        self,
        goal: str,
        project_type: str,
        status: str,
        stages_completed: int,
        project_path: str,
        summary: str,
    ) -> int:
        now = datetime.now(timezone.utc).isoformat()
        clean_goal = redact_secrets(goal)
        clean_summary = redact_secrets(summary)
        if self._use_sqlite:
            try:
                with closing(sqlite3.connect(self.db_path)) as conn:
                    conn.execute("PRAGMA journal_mode=MEMORY;")
                    conn.execute("PRAGMA synchronous=OFF;")
                    cur = conn.execute(
                        """
                        INSERT INTO task_runs (timestamp, goal, project_type, status, stages_completed, project_path, summary)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (now, clean_goal, project_type, status, stages_completed, project_path, clean_summary),
                    )
                    conn.commit()
                    return int(cur.lastrowid)
            except sqlite3.OperationalError:
                self._use_sqlite = False

        data = json.loads(self.runs_fallback_path.read_text(encoding="utf-8"))
        runs = data.setdefault("runs", [])
        run_id = len(runs) + 1
        runs.append(
            {
                "id": run_id,
                "timestamp": now,
                "goal": clean_goal,
                "project_type": project_type,
                "status": status,
                "stages_completed": stages_completed,
                "project_path": project_path,
                "summary": clean_summary,
            }
        )
        self.runs_fallback_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return run_id

    def list_task_runs(self, limit: int = 15) -> List[Dict[str, Any]]:
        if self._use_sqlite:
            try:
                with closing(sqlite3.connect(self.db_path)) as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute("SELECT * FROM task_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
                    return [dict(r) for r in rows]
            except sqlite3.OperationalError:
                self._use_sqlite = False
        data = json.loads(self.runs_fallback_path.read_text(encoding="utf-8"))
        return list(reversed(data.get("runs", [])))[:limit]

    def get_skills(self) -> List[Dict[str, Any]]:
        return json.loads(self.skills_path.read_text(encoding="utf-8")).get("skills", [])

    def get_experiments(self) -> List[Dict[str, Any]]:
        return json.loads(self.experiments_path.read_text(encoding="utf-8")).get("experiments", [])
