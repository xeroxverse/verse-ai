"""
Strict 3-Tier Permission, Approval Queue, and Security Auditing System.
LEVEL_1: Low Risk (Auto-Execute: Research, read files, code analysis, calculations, local tests, memory, planning)
LEVEL_2: Approval Required (Modify external files, shell commands, install deps, git commit, deploy, send messages)
LEVEL_3: Explicit Confirmation (Payments, purchases, deleting data, sharing sensitive info, phone calls, irreversible ops)
"""

from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
import re
from typing import Any, Dict, List, Optional
import uuid


class PermissionLevel(str, Enum):
  LEVEL_1 = "LEVEL_1"
  LEVEL_2 = "LEVEL_2"
  LEVEL_3 = "LEVEL_3"


@dataclass(frozen=True)
class SecurityDecision:
  allowed_immediately: bool
  level: PermissionLevel
  requires_approval: bool
  requires_explicit_confirmation: bool
  reason: str
  sanitized_target: str
  approval_request_id: Optional[str] = None

  def to_dict(self) -> Dict[str, Any]:
    return asdict(self)


SECRET_PATTERNS = [
    (re.compile(r"(AIza[0-9A-Za-z\-_]{20,})"), "[REDACTED_GOOGLE_API_KEY]"),
    (re.compile(r"(gsk_[0-9A-Za-z]{20,})"), "[REDACTED_GROQ_API_KEY]"),
    (re.compile(r"(sk-[0-9A-Za-z\-_]{20,})"), "[REDACTED_OPENAI_KEY]"),
    (
        re.compile(
            r"(?i)(password|passwd|secret|api_key|token)\s*[:=]\s*['\"]?([^'\"\s]{6,})['\"]?"
        ),
        r"\1=[REDACTED_SECRET]",
    ),
]

CATASTROPHIC_PATTERNS = [
    r"(?i)\bFormat-Volume\b",
    r"(?i)\bClear-Disk\b",
    r"(?i)\bdiskpart\b",
    r"(?i)\bbcdedit\b",
    r"(?i)\bRemove-Item\b.*(-Recurse|-Force).*(\\|C:|\*|System32|Windows)",
    r"(?i)\brm\s+-rf\s+(/|~|C:)",
    r"(?i)\bSet-MpPreference\b.*-DisableRealtimeMonitoring\s+\$true",
    r"(?i)\bnetsh\s+advfirewall\s+set\s+allprofiles\s+state\s+off\b",
]

LEVEL_3_PATTERNS = [
    r"(?i)\b(payment|purchase|buy|checkout|stripe|razorpay|upi|transfer_funds)\b",
    r"(?i)\b(Remove-Item|del|rmdir|unlink|DROP\s+TABLE|DELETE\s+FROM)\b",
    r"(?i)\b(share_credentials|export_private_key|make_phone_call|twilio)\b",
    r"(?i)\b(reg\s+delete|Stop-Computer|Restart-Computer)\b",
]

LEVEL_2_PATTERNS = [
    r"(?i)\b(pip\s+install|winget\s+install|npm\s+install)\b",
    r"(?i)\b(git\s+commit|git\s+push|deploy|publish)\b",
    r"(?i)\b(send_email|send_message|smtp|webhook)\b",
    r"(?i)\b(powershell|cmd\.exe|Invoke-WebRequest|Start-Process)\b",
]


def redact_secrets(text: str) -> str:
  """Scrubs API keys, tokens, and passwords so credentials are never exposed in logs or UI."""
  cleaned = text or ""
  for regex, replacement in SECRET_PATTERNS:
    cleaned = regex.sub(replacement, cleaned)
  return cleaned


class PermissionManager:
  """Enforces LEVEL_1 / LEVEL_2 / LEVEL_3 rules and maintains an interactive approval queue."""

  def __init__(self):
    self._pending_approvals: Dict[str, Dict[str, Any]] = {}
    self._approved_tokens: set[str] = set()

  def evaluate(
      self,
      action_type: str,
      command_or_detail: str,
      approval_token: Optional[str] = None,
      explicit_confirm_phrase: Optional[str] = None,
  ) -> SecurityDecision:
    sanitized = redact_secrets(command_or_detail.strip())
    if not sanitized:
      return SecurityDecision(
          False, PermissionLevel.LEVEL_1, False, False, "Empty command rejected.", ""
      )

    for pat in CATASTROPHIC_PATTERNS:
      if re.search(pat, command_or_detail):
        return SecurityDecision(
            allowed_immediately=False,
            level=PermissionLevel.LEVEL_3,
            requires_approval=False,
            requires_explicit_confirmation=True,
            reason=(
                "HARD BLOCKED catastrophic system/security command matching:"
                f" {pat}"
            ),
            sanitized_target=sanitized,
        )

    for pat in LEVEL_3_PATTERNS:
      if re.search(pat, command_or_detail) or action_type.lower() in {
          "payment",
          "delete_data",
          "external_call",
      }:
        if explicit_confirm_phrase == "CONFIRM_LEVEL_3":
          return SecurityDecision(
              allowed_immediately=True,
              level=PermissionLevel.LEVEL_3,
              requires_approval=False,
              requires_explicit_confirmation=True,
              reason=(
                  "LEVEL_3 action explicitly confirmed by user with"
                  " CONFIRM_LEVEL_3."
              ),
              sanitized_target=sanitized,
          )
        req_id = self._enqueue(PermissionLevel.LEVEL_3, action_type, sanitized)
        return SecurityDecision(
            allowed_immediately=False,
            level=PermissionLevel.LEVEL_3,
            requires_approval=True,
            requires_explicit_confirmation=True,
            reason=(
                "LEVEL_3 high-risk operation requires explicit confirmation"
                " ('CONFIRM_LEVEL_3')."
            ),
            sanitized_target=sanitized,
            approval_request_id=req_id,
        )

    for pat in LEVEL_2_PATTERNS:
      if re.search(pat, command_or_detail) or action_type.lower() in {
          "shell_exec",
          "install_dep",
          "git_commit",
          "modify_important_file",
      }:
        if approval_token and approval_token in self._approved_tokens:
          return SecurityDecision(
              allowed_immediately=True,
              level=PermissionLevel.LEVEL_2,
              requires_approval=True,
              requires_explicit_confirmation=False,
              reason=f"LEVEL_2 operation approved via token {approval_token}.",
              sanitized_target=sanitized,
          )
        req_id = self._enqueue(PermissionLevel.LEVEL_2, action_type, sanitized)
        return SecurityDecision(
            allowed_immediately=False,
            level=PermissionLevel.LEVEL_2,
            requires_approval=True,
            requires_explicit_confirmation=False,
            reason="LEVEL_2 operation paused pending user approval.",
            sanitized_target=sanitized,
            approval_request_id=req_id,
        )

    return SecurityDecision(
        allowed_immediately=True,
        level=PermissionLevel.LEVEL_1,
        requires_approval=False,
        requires_explicit_confirmation=False,
        reason="LEVEL_1 low-risk operation permitted automatically.",
        sanitized_target=sanitized,
    )

  def _enqueue(
      self, level: PermissionLevel, action_type: str, detail: str
  ) -> str:
    req_id = f"req_{uuid.uuid4().hex[:8]}"
    self._pending_approvals[req_id] = {
        "request_id": req_id,
        "level": level.value,
        "action_type": action_type,
        "detail": detail,
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return req_id

  def approve_request(
      self, request_id: str, explicit_confirm_phrase: Optional[str] = None
  ) -> Dict[str, Any]:
    req = self._pending_approvals.get(request_id)
    if not req:
      return {"status": "NOT_FOUND", "request_id": request_id}
    if (
        req["level"] == PermissionLevel.LEVEL_3.value
        and explicit_confirm_phrase != "CONFIRM_LEVEL_3"
    ):
      return {
          "status": "CONFIRMATION_REQUIRED",
          "request_id": request_id,
          "message": (
              "LEVEL_3 requires explicit_confirm_phrase='CONFIRM_LEVEL_3'."
          ),
      }
    req["status"] = "APPROVED"
    self._approved_tokens.add(request_id)
    return req

  def reject_request(self, request_id: str) -> Dict[str, Any]:
    req = self._pending_approvals.get(request_id)
    if not req:
      return {"status": "NOT_FOUND", "request_id": request_id}
    req["status"] = "REJECTED"
    return req

  def list_pending(self) -> List[Dict[str, Any]]:
    return list(self._pending_approvals.values())

  def audit_code_security(self, code: str) -> Dict[str, Any]:
    """Static vulnerability scanner run by the Security AI Agent."""
    findings: List[str] = []
    if re.search(r"\beval\s*\(", code):
      findings.append("Avoid raw eval() on untrusted input.")
    if re.search(r"shell\s*=\s*True", code) and "evaluate(" not in code:
      findings.append("Subprocess shell=True detected without permission gate.")
    for regex, label in SECRET_PATTERNS:
      if regex.search(code):
        findings.append(f"Potential hardcoded secret detected ({label}).")
    return {
        "passed": len(findings) == 0,
        "risk_score": "LOW" if len(findings) == 0 else "MEDIUM",
        "findings": findings,
    }
