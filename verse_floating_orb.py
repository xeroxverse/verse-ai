#!/usr/bin/env python3
"""
VERSE AI — Desktop Orb Module (Disabled by default for Clean Single-Window Professional HUD).
Retains state definitions (Idle, Listening, Thinking, Working, Speaking, Error) for system compatibility
without opening any floating desktop popup window.
"""

from __future__ import annotations

STATE_PALETTES = {
    "Idle": ("#00e5ff", "#0088ff", "#ffaa00", 0.040),
    "Listening": ("#00ff9d", "#10b981", "#00e5ff", 0.095),
    "Thinking": ("#c084fc", "#9333ea", "#00e5ff", 0.140),
    "Working": ("#00e5ff", "#0284c7", "#ffaa00", 0.105),
    "Speaking": ("#38bdf8", "#00e5ff", "#ffaa00", 0.095),
    "Error": ("#ff2a54", "#dc2626", "#ffaa00", 0.120),
}

STATUS_BANNER = "VERSE AI // CLEAN_HUD_MODE (Floating Popup Disabled)"


def launch_floating_orb(dashboard_url: str = "http://127.0.0.1:8765") -> int:
    # Intentionally disabled per user request so no floating idle widget clutters the desktop
    return 0


if __name__ == "__main__":
    raise SystemExit(0)
