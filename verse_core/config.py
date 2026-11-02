"""Hardware & System Configuration for Acer Swift Pro (Intel Core Ultra 5 125H, 16GB LPDDR5X, No NVIDIA CUDA)."""

from __future__ import annotations
from dataclasses import asdict, dataclass, field
import json
import os
from pathlib import Path
from typing import Any, Dict


@dataclass
class HardwareSpec:
    laptop_model: str = "Acer Swift Pro"
    cpu_model: str = "Intel Core Ultra 5 125H"
    igpu_model: str = "Intel Arc Integrated Graphics"
    npu_model: str = "Intel AI Boost NPU"
    has_nvidia_cuda: bool = False  # Never assume CUDA on this hardware
    total_ram_gb: float = 16.0
    ram_speed_mts: int = 6400
    safe_ram_budget_gb: float = 10.5  # Leaves 5.5 GB for Windows 11 + browser + desktop
    max_single_model_ram_gb: float = 4.8  # Q4_K_M 7B or 3B GGUF limit
    max_cpu_threads: int = 6  # Optimal across Ultra 5 125H P-cores without thermal throttling
    prefer_quantization: str = "Q4_K_M"
    supported_backends: tuple[str, ...] = ("cpu_avx2_vnni", "intel_sycl_igpu", "openvino_npu", "ollama", "llamacpp")


@dataclass
class VerseConfig:
    root_dir: Path = field(default_factory=lambda: Path(os.environ.get("VERSE_HOME", Path.cwd())))
    host: str = field(default_factory=lambda: os.environ.get("VERSE_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(os.environ.get("VERSE_PORT", "8765")))
    ollama_base_url: str = field(default_factory=lambda: os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434"))
    llamacpp_base_url: str = field(default_factory=lambda: os.environ.get("LLAMACPP_HOST", "http://127.0.0.1:8080"))
    default_fast_model: str = field(default_factory=lambda: os.environ.get("VERSE_FAST_MODEL", "qwen2.5:1.5b-instruct-q4_K_M"))
    default_coder_model: str = field(default_factory=lambda: os.environ.get("VERSE_CODER_MODEL", "qwen2.5-coder:3b-instruct-q4_K_M"))
    heavy_coder_model: str = field(default_factory=lambda: os.environ.get("VERSE_HEAVY_MODEL", "qwen2.5-coder:7b-instruct-q4_K_M"))
    sequential_model_loading: bool = True
    hardware: HardwareSpec = field(default_factory=HardwareSpec)

    @property
    def workspace_dir(self) -> Path:
        p = self.root_dir / "workspace"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def projects_dir(self) -> Path:
        p = self.workspace_dir / "projects"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def memory_dir(self) -> Path:
        p = self.root_dir / "memory"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def backup_dir(self) -> Path:
        p = self.root_dir / "backups"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def models_dir(self) -> Path:
        p = self.root_dir / "models"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def configs_dir(self) -> Path:
        p = self.root_dir / "configs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["root_dir"] = str(self.root_dir)
        return data
