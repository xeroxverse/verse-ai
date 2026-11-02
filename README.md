# PROJECT VERSE — Master AI Orchestrator (v4.0)

**Hardware Target**: Acer Swift Pro • Intel Core Ultra 5 125H • 16 GB LPDDR5X (6400 MT/s) • Intel Arc Integrated Graphics + Intel AI Boost NPU • Windows 11 PowerShell (Zero NVIDIA CUDA dependency).

## Key Capabilities
1. **8-Agent AI Company Hierarchy**: `CEO AI`, `Research AI`, `UI/UX Designer AI`, `Coder AI`, `Tester AI`, `Security AI`, `Voice AI`, and `Employee AI Sub-Agents`.
2. **11-Stage Autonomous Workflow**: `UNDERSTAND -> PLAN -> RESEARCH -> ASSIGN -> EXECUTE -> TEST -> FIX -> SECURITY REVIEW -> VERIFY -> DELIVER -> LEARN`.
3. **JARVIS Futuristic Interface + Floating AI Orb**:
   - Browser HUD (`ui/jarvis_dashboard.html` at `http://127.0.0.1:8765`) with draggable/minimizable 60 FPS Canvas Orb (`Idle`, `Listening`, `Thinking`, `Working`, `Speaking`, `Error`), Light/Dark themes, and keyboard shortcuts (`Ctrl+K`, `Alt+V`, `Alt+O`, `Alt+T`).
   - Native Windows Always-on-Top Transparent Floating Orb (`verse_floating_orb.py`).
4. **Strict Permission & Security System**: `LEVEL_1` (Auto), `LEVEL_2` (User Approval Queue), `LEVEL_3` (Explicit `CONFIRM_LEVEL_3` Gate), and automatic API key/secret redaction.
5. **Controlled Self-Improvement**: Tracks skills (`memory/skills.json`), experiments (`memory/experiments.json`), and agent scorecards (`memory/agent_metrics.json`) with pre-change backups and automatic rollback on safety regression.
6. **Preserved Single-File Compatibility**: `verse_ai.py` remains intact alongside the modular `verse.py` + `verse_core/` architecture.
