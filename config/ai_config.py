"""
AI Configuration and Auto-Detection

Automatically detects hardware capabilities and configures optimal AI model settings.
"""

import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class Hardware:
    """Hardware capabilities"""

    has_cuda: bool = False
    gpu_name: str = ""
    vram_gb: float = 0.0
    ram_gb: float = 0.0
    cpu_cores: int = 0
    os_name: str = ""


@dataclass
class AIConfig:
    """AI model configuration"""

    # LLM settings
    llm_enabled: bool = True
    llm_model_path: Optional[str] = None
    llm_n_ctx: int = 2048
    llm_n_threads: int = 4
    llm_n_gpu_layers: int = 0

    # Large LLM for scripting
    llm_scripting_enabled: bool = False
    llm_scripting_model_path: Optional[str] = None
    llm_scripting_n_ctx: int = 4096
    llm_scripting_n_threads: int = 8

    # Stable Diffusion settings
    sd_enabled: bool = False
    sd_model_id: str = "runwayml/stable-diffusion-v1-5"
    sd_torch_dtype: str = "float16"  # float16 for GPU, float32 for CPU
    sd_num_inference_steps: int = 20
    sd_guidance_scale: float = 7.5

    # Memory optimizations
    sd_enable_attention_slicing: bool = True
    sd_enable_vae_slicing: bool = True
    sd_enable_xformers: bool = False
    sd_enable_model_cpu_offload: bool = False
    sd_enable_sequential_cpu_offload: bool = False

    # Animation generation
    default_use_ai: bool = False  # Default to procedural
    cache_enabled: bool = True

    # Hardware
    hardware: Hardware = None


class HardwareDetector:
    """Detect hardware capabilities"""

    @staticmethod
    def detect() -> Hardware:
        """Detect current hardware"""

        hardware = Hardware()

        # OS
        hardware.os_name = platform.system()

        # CPU
        try:
            hardware.cpu_cores = os.cpu_count() or 4
        except:
            hardware.cpu_cores = 4

        # RAM
        try:
            if platform.system() == "Linux":
                with open("/proc/meminfo") as f:
                    mem_kb = int(f.readline().split()[1])
                    hardware.ram_gb = mem_kb / (1024 * 1024)
            elif platform.system() == "Darwin":  # macOS
                import subprocess

                result = subprocess.check_output(["sysctl", "hw.memsize"])
                mem_bytes = int(result.split()[1])
                hardware.ram_gb = mem_bytes / (1024**3)
            elif platform.system() == "Windows":
                import ctypes

                kernel32 = ctypes.windll.kernel32
                c_ulong = ctypes.c_ulong

                class MEMORYSTATUS(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", c_ulong),
                        ("dwMemoryLoad", c_ulong),
                        ("dwTotalPhys", c_ulong),
                        ("dwAvailPhys", c_ulong),
                        ("dwTotalPageFile", c_ulong),
                        ("dwAvailPageFile", c_ulong),
                        ("dwTotalVirtual", c_ulong),
                        ("dwAvailVirtual", c_ulong),
                    ]

                memory_status = MEMORYSTATUS()
                memory_status.dwLength = ctypes.sizeof(MEMORYSTATUS)
                kernel32.GlobalMemoryStatus(ctypes.byref(memory_status))
                hardware.ram_gb = memory_status.dwTotalPhys / (1024**3)
        except:
            hardware.ram_gb = 8.0  # Default assumption

        # CUDA / GPU
        try:
            import torch

            if torch.cuda.is_available():
                hardware.has_cuda = True
                hardware.gpu_name = torch.cuda.get_device_name(0)
                hardware.vram_gb = (
                    torch.cuda.get_device_properties(0).total_memory / 1e9
                )
        except ImportError:
            hardware.has_cuda = False

        return hardware


class AIConfigManager:
    """Manage AI configuration with auto-detection"""

    def __init__(self, auto_detect: bool = True):
        """
        Initialize configuration manager.

        Args:
            auto_detect: Automatically detect hardware and configure
        """
        self.hardware = HardwareDetector.detect()
        self.config = AIConfig(hardware=self.hardware)

        if auto_detect:
            self._auto_configure()

    def _auto_configure(self):
        """Automatically configure based on detected hardware"""

        print("\n" + "=" * 70)
        print("  AI CONFIGURATION AUTO-DETECTION")
        print("=" * 70)

        # Hardware summary
        print(f"\nDetected Hardware:")
        print(f"  OS: {self.hardware.os_name}")
        print(f"  CPU Cores: {self.hardware.cpu_cores}")
        print(f"  RAM: {self.hardware.ram_gb:.1f} GB")

        if self.hardware.has_cuda:
            print(f"  GPU: {self.hardware.gpu_name}")
            print(f"  VRAM: {self.hardware.vram_gb:.1f} GB")
        else:
            print(f"  GPU: None")

        # Configure LLM
        self._configure_llm()

        # Configure Stable Diffusion
        self._configure_sd()

        print("\n" + "=" * 70)

    def _configure_llm(self):
        """Configure LLM based on hardware"""

        print(f"\nLLM Configuration:")

        # Check if models exist
        models_dir = Path("models")

        # Standard LLM
        llm_candidates = [
            ("phi-3-mini-q4.gguf", "Phi-3 Mini", 2048, False),
            ("llama-3.2-3b-q4.gguf", "Llama 3.2 3B", 2048, False),
            ("llama-3.2-1b-q4.gguf", "Llama 3.2 1B", 2048, False),
            ("tinyllama-1.1b-q4.gguf", "TinyLlama", 2048, False),
        ]

        for filename, name, n_ctx, _ in llm_candidates:
            path = models_dir / filename
            if path.exists():
                self.config.llm_enabled = True
                self.config.llm_model_path = str(path)
                self.config.llm_n_ctx = n_ctx
                print(f"  ✓ Found: {name}")
                print(f"    Path: {path}")
                break
        else:
            print(f"  ✗ No LLM model found")
            print(f"    Download with: python scripts/download_models.py --recommended")
            self.config.llm_enabled = False

        # Large LLM for scripting
        scripting_model = models_dir / "llama-3.2-8b-q4.gguf"
        if scripting_model.exists():
            self.config.llm_scripting_enabled = True
            self.config.llm_scripting_model_path = str(scripting_model)
            print(f"  ✓ Animation scripting: Llama 3.2 8B")
        else:
            print(f"  ✗ No scripting LLM (optional)")
            print(f"    Download with: python scripts/download_models.py --model llama-3.2-8b")

        # Thread optimization
        self.config.llm_n_threads = min(self.hardware.cpu_cores, 8)
        self.config.llm_scripting_n_threads = min(self.hardware.cpu_cores, 8)

        # GPU offloading (if CUDA available)
        if self.hardware.has_cuda and self.hardware.vram_gb >= 6:
            self.config.llm_n_gpu_layers = 35  # Full offload
            print(f"  GPU offload: Enabled (VRAM: {self.hardware.vram_gb:.1f} GB)")
        else:
            self.config.llm_n_gpu_layers = 0
            print(f"  GPU offload: Disabled (CPU only)")

    def _configure_sd(self):
        """Configure Stable Diffusion based on hardware"""

        print(f"\nStable Diffusion Configuration:")

        if not self.hardware.has_cuda:
            print(f"  ✗ No GPU detected - SD disabled")
            print(f"    Stable Diffusion requires NVIDIA GPU with 6+ GB VRAM")
            self.config.sd_enabled = False
            return

        vram = self.hardware.vram_gb

        if vram < 6:
            print(f"  ✗ Insufficient VRAM ({vram:.1f} GB < 6 GB required)")
            self.config.sd_enabled = False
            return

        # Enable Stable Diffusion
        self.config.sd_enabled = True
        print(f"  ✓ Stable Diffusion enabled")
        print(f"    Model: {self.config.sd_model_id}")

        # Configure based on VRAM
        if vram >= 12:
            # High-end GPU (RTX 4070+, RTX 3080+)
            self.config.sd_num_inference_steps = 30
            self.config.sd_enable_xformers = True
            self.config.default_use_ai = True
            print(f"  Tier: High-end ({vram:.1f} GB VRAM)")
            print(f"  Quality: High (30 steps)")
            print(f"  Default mode: AI generation")

        elif vram >= 8:
            # Mid-range GPU (RTX 4060, RTX 3060 Ti, RTX 3070)
            self.config.sd_num_inference_steps = 25
            self.config.sd_enable_xformers = True
            print(f"  Tier: Mid-range ({vram:.1f} GB VRAM)")
            print(f"  Quality: Good (25 steps)")
            print(f"  Default mode: Procedural (AI available)")

        elif vram >= 6:
            # Entry GPU (RTX 3060, GTX 1660 Ti)
            self.config.sd_num_inference_steps = 20
            self.config.sd_enable_model_cpu_offload = True
            print(f"  Tier: Entry ({vram:.1f} GB VRAM)")
            print(f"  Quality: Medium (20 steps)")
            print(f"  Memory: CPU offload enabled")

        else:
            # Low VRAM
            self.config.sd_num_inference_steps = 15
            self.config.sd_enable_sequential_cpu_offload = True
            print(f"  Tier: Low VRAM ({vram:.1f} GB)")
            print(f"  Quality: Fast (15 steps)")
            print(f"  Memory: Sequential CPU offload")

        # Always enable memory optimizations
        self.config.sd_enable_attention_slicing = True
        self.config.sd_enable_vae_slicing = True

    def get_config(self) -> AIConfig:
        """Get current configuration"""
        return self.config

    def print_summary(self):
        """Print configuration summary"""

        print("\n" + "=" * 70)
        print("  AI CONFIGURATION SUMMARY")
        print("=" * 70)

        print(f"\nLLM (Natural Language):")
        if self.config.llm_enabled:
            print(f"  ✓ Enabled")
            print(f"    Model: {Path(self.config.llm_model_path).name}")
            print(f"    Threads: {self.config.llm_n_threads}")
            print(f"    GPU Layers: {self.config.llm_n_gpu_layers}")
        else:
            print(f"  ✗ Disabled (no model found)")

        print(f"\nAnimation Scripting:")
        if self.config.llm_scripting_enabled:
            print(f"  ✓ Enabled (Llama 3.2 8B)")
        else:
            print(f"  ✗ Disabled (download llama-3.2-8b for scripting)")

        print(f"\nStable Diffusion (Sprite Generation):")
        if self.config.sd_enabled:
            print(f"  ✓ Enabled")
            print(f"    Steps: {self.config.sd_num_inference_steps}")
            print(f"    Default mode: {'AI' if self.config.default_use_ai else 'Procedural'}")
        else:
            print(f"  ✗ Disabled (requires GPU)")

        print(f"\nRecommendations:")

        if not self.config.llm_enabled:
            print(f"  • Download LLM: python scripts/download_models.py --recommended")

        if not self.config.llm_scripting_enabled:
            print(
                f"  • For animation scripting: python scripts/download_models.py --model llama-3.2-8b"
            )

        if not self.config.sd_enabled and not self.hardware.has_cuda:
            print(f"  • For AI sprite generation, you need an NVIDIA GPU with 6+ GB VRAM")

        if self.config.sd_enabled and not self.config.sd_enable_xformers:
            print(f"  • For 20-30% speed boost: pip install xformers")

        print("\n" + "=" * 70)


# Singleton instance
_config_manager = None


def get_ai_config(auto_detect: bool = True) -> AIConfig:
    """
    Get AI configuration (singleton).

    Args:
        auto_detect: Auto-detect hardware on first call

    Returns:
        AI Configuration
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = AIConfigManager(auto_detect=auto_detect)

    return _config_manager.get_config()


def print_ai_config():
    """Print AI configuration summary"""
    global _config_manager

    if _config_manager is None:
        _config_manager = AIConfigManager(auto_detect=True)

    _config_manager.print_summary()


# CLI interface
if __name__ == "__main__":
    print_ai_config()
