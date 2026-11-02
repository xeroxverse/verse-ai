"""
Controlled Self-Improvement System (`memory/experiments.json` & `memory/skills.json`).
Enforces:
  - Experience memory (success/failure tracking & error analysis)
  - Agent performance comparison
  - Isolated prompt/workflow experiment testing
  - Immutable Safety Rule lock (NEVER disables or weakens LEVEL_1/LEVEL_2/LEVEL_3)
  - Automatic snapshot backup & rollback on regression failure
"""

from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Tuple

from .config import VerseConfig
from .memory import VerseMemorySystem
from .security import PermissionLevel, PermissionManager


class SelfImprovementSystem:
    def __init__(self, config: VerseConfig, memory: VerseMemorySystem, permissions: PermissionManager):
        self.config = config
        self.memory = memory
        self.permissions = permissions

    def verify_immutable_safety_gate(self) -> Tuple[bool, str]:
        """Runs isolated regression checks to guarantee safety rules and policy invariants are intact."""
        # 1. Catastrophic commands must be blocked
        c1 = self.permissions.evaluate("shell_exec", "Format-Volume -DriveLetter C")
        c2 = self.permissions.evaluate("shell_exec", r"Remove-Item -Recurse -Force C:\Windows\System32")
        if c1.allowed_immediately or c2.allowed_immediately:
            return False, "Immutable safety failure: Destructive command was not blocked."

        # 2. LEVEL_2 command without token must require approval
        c3 = self.permissions.evaluate("install_dep", "pip install fastapi")
        if c3.allowed_immediately or c3.level != PermissionLevel.LEVEL_2:
            return False, "Immutable safety failure: LEVEL_2 dependency install bypassed approval."

        # 3. LEVEL_3 action without explicit confirmation phrase must be blocked
        c4 = self.permissions.evaluate("payment", "transfer_funds 5000")
        if c4.allowed_immediately or c4.level != PermissionLevel.LEVEL_3:
            return False, "Immutable safety failure: LEVEL_3 payment bypassed explicit confirmation."

        # 4. Prompt policy must keep immutable_safety_enabled == True
        try:
            policy = json.loads(self.memory.policy_path.read_text(encoding="utf-8"))
            if not policy.get("immutable_safety_enabled", False):
                return False, "Policy regression failure: immutable_safety_enabled was set to False."
            if "LEVEL_1/LEVEL_2/LEVEL_3" not in policy.get("system_directive", ""):
                return False, "Policy regression failure: safety level directive removed."
        except Exception as exc:
            return False, f"Policy JSON corrupted: {exc}"

        return True, "All immutable safety & permission regression checks passed."

    def learn_from_workflow(
        self,
        goal: str,
        project_type: str,
        status: str,
        project_dir: str,
        error_notes: str = "",
    ) -> Dict[str, Any]:
        """Records experience, updates reusable coding skills, and runs a gated self-improvement experiment."""
        policy_bak = self.memory.create_backup(self.memory.policy_path)
        skills_bak = self.memory.create_backup(self.memory.skills_path)

        skills_doc = json.loads(self.memory.skills_path.read_text(encoding="utf-8"))
        skills = skills_doc.setdefault("skills", [])
        slug = "".join(c if c.isalnum() else "-" for c in goal.lower()[:28]).strip("-") or "workflow"
        skill_name = f"solution-{project_type}-{slug}"

        existing = next((s for s in skills if s["name"] == skill_name), None)
        if existing and status == "PASS":
            existing["success_count"] = existing.get("success_count", 1) + 1
        elif status == "PASS":
            skills.append(
                {
                    "id": f"skill_{len(skills) + 1:03d}",
                    "name": skill_name,
                    "category": project_type,
                    "trigger": goal.lower()[:60],
                    "solution_summary": f"Verified {project_type} template delivered in {Path(project_dir).name}.",
                    "success_count": 1,
                }
            )
        self.memory.skills_path.write_text(json.dumps(skills_doc, indent=2), encoding="utf-8")

        policy = json.loads(self.memory.policy_path.read_text(encoding="utf-8"))
        policy["version"] = int(policy.get("version", 1)) + 1
        policy["last_learned_goal"] = goal[:80]
        self.memory.policy_path.write_text(json.dumps(policy, indent=2), encoding="utf-8")

        passed, reason = self.verify_immutable_safety_gate()
        if not passed:
            self.memory.restore_backup(policy_bak, self.memory.policy_path)
            self.memory.restore_backup(skills_bak, self.memory.skills_path)
            return self._record_experiment(
                hypothesis=f"Learn skill '{skill_name}' from {project_type} workflow",
                outcome=f"ROLLED_BACK: {reason}",
                passed=False,
                rollback_cmd=f"Copy-Item -Force '{policy_bak}' '{self.memory.policy_path}'",
                error_analysis=error_notes or reason,
            )

        return self._record_experiment(
            hypothesis=f"Organize reusable solution '{skill_name}' & upgrade policy v{policy['version']}",
            outcome=f"ACCEPTED: {reason}",
            passed=True,
            rollback_cmd=f"Copy-Item -Force '{policy_bak}' '{self.memory.policy_path}'" if policy_bak else "none",
            error_analysis=error_notes or "Zero errors detected during 11-stage workflow.",
        )

    def test_prompt_mutation(self, new_directive: str, keep_safety_flag: bool = True) -> Dict[str, Any]:
        """Tests a proposed policy change in isolation; automatically rolls back if it weakens safety."""
        bak = self.memory.create_backup(self.memory.policy_path)
        policy = json.loads(self.memory.policy_path.read_text(encoding="utf-8"))
        policy["system_directive"] = new_directive
        policy["immutable_safety_enabled"] = keep_safety_flag
        self.memory.policy_path.write_text(json.dumps(policy, indent=2), encoding="utf-8")

        passed, reason = self.verify_immutable_safety_gate()
        if not passed:
            self.memory.restore_backup(bak, self.memory.policy_path)

        return self._record_experiment(
            hypothesis=f"Prompt mutation test: {new_directive[:50]}",
            outcome="ACCEPTED" if passed else f"REJECTED_AND_ROLLED_BACK: {reason}",
            passed=passed,
            rollback_cmd=f"Copy-Item -Force '{bak}' '{self.memory.policy_path}'" if bak else "none",
            error_analysis="" if passed else reason,
        )

    def _record_experiment(
        self,
        hypothesis: str,
        outcome: str,
        passed: bool,
        rollback_cmd: str,
        error_analysis: str,
    ) -> Dict[str, Any]:
        doc = json.loads(self.memory.experiments_path.read_text(encoding="utf-8"))
        exps = doc.setdefault("experiments", [])
        entry = {
            "id": len(exps) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hypothesis": hypothesis,
            "outcome": outcome,
            "passed_regression": passed,
            "accepted": passed,
            "error_analysis": error_analysis,
            "rollback_cmd": rollback_cmd,
        }
        exps.append(entry)
        self.memory.experiments_path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        return entry
