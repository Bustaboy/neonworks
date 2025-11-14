#!/usr/bin/env python3
"""
Model Download Utility

Downloads AI models for NeonWorks animation system.
Automatically detects hardware and downloads appropriate models.
"""

import os
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional


class ModelDownloader:
    """Download and manage AI models"""

    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)

        # Model registry
        self.available_models = {
            # LLM Models (for natural language interpretation)
            "phi-3-mini": {
                "name": "Phi-3 Mini 3.8B (4-bit)",
                "size": "2.3 GB",
                "url": "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf",
                "filename": "phi-3-mini-q4.gguf",
                "type": "llm",
                "hardware": "CPU (5 GB RAM)",
                "speed": "30-60 tok/s",
                "license": "MIT",
                "recommended": True,
            },
            "llama-3.2-3b": {
                "name": "Llama 3.2 3B (4-bit)",
                "size": "3.2 GB",
                "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                "filename": "llama-3.2-3b-q4.gguf",
                "type": "llm",
                "hardware": "CPU (6 GB RAM)",
                "speed": "20-40 tok/s",
                "license": "Meta",
                "recommended": False,
            },
            "llama-3.2-1b": {
                "name": "Llama 3.2 1B (4-bit)",
                "size": "1.0 GB",
                "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
                "filename": "llama-3.2-1b-q4.gguf",
                "type": "llm",
                "hardware": "CPU (3 GB RAM)",
                "speed": "40-80 tok/s",
                "license": "Meta",
                "recommended": False,
            },
            "tinyllama": {
                "name": "TinyLlama 1.1B (4-bit)",
                "size": "700 MB",
                "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                "filename": "tinyllama-1.1b-q4.gguf",
                "type": "llm",
                "hardware": "CPU (2 GB RAM)",
                "speed": "50-100 tok/s",
                "license": "Apache 2.0",
                "recommended": False,
            },
            # Animation scripting (larger LLM for complex parsing)
            "llama-3.2-8b": {
                "name": "Llama 3.2 8B (4-bit) - For Animation Scripting",
                "size": "8.5 GB",
                "url": "https://huggingface.co/lmstudio-community/Llama-3.2-8B-Instruct-GGUF/resolve/main/Llama-3.2-8B-Instruct-Q4_K_M.gguf",
                "filename": "llama-3.2-8b-q4.gguf",
                "type": "llm_scripting",
                "hardware": "CPU (12 GB RAM) or GPU",
                "speed": "10-20 tok/s",
                "license": "Meta",
                "recommended": True,
                "description": "Better reasoning for complex animation scripts",
            },
        }

    def list_models(self, model_type: Optional[str] = None):
        """List available models"""
        print("\n" + "=" * 70)
        print("  AVAILABLE AI MODELS FOR NEONWORKS")
        print("=" * 70)

        categories = {
            "llm": "Natural Language Interpretation (Required)",
            "llm_scripting": "Animation Scripting (Optional)",
            "vision": "Sprite Generation (Requires GPU)",
        }

        for cat_type, cat_name in categories.items():
            if model_type and cat_type != model_type:
                continue

            models = [m for m in self.available_models.values() if m["type"] == cat_type]
            if not models:
                continue

            print(f"\n📦 {cat_name}")
            print("-" * 70)

            for model in models:
                status = "✓ RECOMMENDED" if model.get("recommended") else "  Optional"
                print(f"\n{status}")
                print(f"  Name: {model['name']}")
                print(f"  Size: {model['size']}")
                print(f"  Hardware: {model['hardware']}")
                print(f"  Speed: {model['speed']}")
                print(f"  License: {model['license']}")
                if "description" in model:
                    print(f"  Note: {model['description']}")

        print("\n" + "=" * 70)

    def download_model(self, model_id: str, force: bool = False) -> bool:
        """Download a specific model"""
        if model_id not in self.available_models:
            print(f"❌ Unknown model: {model_id}")
            print(f"Available models: {', '.join(self.available_models.keys())}")
            return False

        model = self.available_models[model_id]
        output_path = self.models_dir / model["filename"]

        # Check if already downloaded
        if output_path.exists() and not force:
            print(f"✓ Model already downloaded: {output_path}")
            return True

        print(f"\n📥 Downloading {model['name']}")
        print(f"   Size: {model['size']}")
        print(f"   URL: {model['url']}")
        print(f"   Output: {output_path}")

        try:
            # Download with progress
            self._download_with_progress(model["url"], output_path)
            print(f"\n✓ Successfully downloaded: {output_path}")
            return True

        except Exception as e:
            print(f"\n❌ Download failed: {e}")
            if output_path.exists():
                output_path.unlink()  # Clean up partial download
            return False

    def _download_with_progress(self, url: str, output_path: Path):
        """Download file with progress bar"""

        def reporthook(count, block_size, total_size):
            """Progress callback"""
            if total_size > 0:
                percent = min(int(count * block_size * 100 / total_size), 100)
                mb_downloaded = count * block_size / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)

                bar_length = 50
                filled = int(bar_length * percent / 100)
                bar = "=" * filled + "-" * (bar_length - filled)

                sys.stdout.write(
                    f"\r   [{bar}] {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)"
                )
                sys.stdout.flush()

        urllib.request.urlretrieve(url, output_path, reporthook=reporthook)

    def download_recommended(self) -> bool:
        """Download all recommended models"""
        print("\n🚀 Downloading recommended models for NeonWorks...\n")

        recommended = [
            model_id
            for model_id, model in self.available_models.items()
            if model.get("recommended", False)
        ]

        print(f"Will download {len(recommended)} models:")
        for model_id in recommended:
            model = self.available_models[model_id]
            print(f"  • {model['name']} ({model['size']})")

        print()
        response = input("Continue? (y/n): ").strip().lower()
        if response != "y":
            print("Cancelled.")
            return False

        success = True
        for model_id in recommended:
            if not self.download_model(model_id):
                success = False

        if success:
            print("\n" + "=" * 70)
            print("  ✓ ALL RECOMMENDED MODELS DOWNLOADED")
            print("=" * 70)
            print("\nYou can now use:")
            print("  • Natural language animation requests (Phi-3 Mini)")
            print("  • Animation scripting (Llama 3.2 8B)")
            print("\nNext steps:")
            print("  1. Test LLM: python scripts/test_llm.py")
            print("  2. Test scripting: python scripts/test_animation_scripting.py")
            print("  3. Install Stable Diffusion (for sprite generation):")
            print("     pip install diffusers transformers accelerate")

        return success

    def check_downloaded_models(self) -> Dict[str, bool]:
        """Check which models are already downloaded"""
        status = {}

        for model_id, model in self.available_models.items():
            path = self.models_dir / model["filename"]
            status[model_id] = path.exists()

        return status

    def get_model_path(self, model_id: str) -> Optional[Path]:
        """Get path to downloaded model"""
        if model_id not in self.available_models:
            return None

        path = self.models_dir / self.available_models[model_id]["filename"]
        return path if path.exists() else None


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download AI models for NeonWorks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available models
  python download_models.py --list

  # Download recommended models
  python download_models.py --recommended

  # Download specific model
  python download_models.py --model phi-3-mini

  # Download animation scripting model
  python download_models.py --model llama-3.2-8b

  # Check what's already downloaded
  python download_models.py --check
        """,
    )

    parser.add_argument(
        "--list", action="store_true", help="List available models"
    )

    parser.add_argument(
        "--recommended",
        action="store_true",
        help="Download all recommended models",
    )

    parser.add_argument("--model", type=str, help="Download specific model")

    parser.add_argument(
        "--check", action="store_true", help="Check downloaded models"
    )

    parser.add_argument(
        "--models-dir",
        type=str,
        default="models",
        help="Models directory (default: models/)",
    )

    args = parser.parse_args()

    downloader = ModelDownloader(models_dir=args.models_dir)

    if args.list:
        downloader.list_models()
        return

    if args.check:
        print("\n📋 Downloaded Models Status")
        print("=" * 70)
        status = downloader.check_downloaded_models()

        for model_id, is_downloaded in status.items():
            model = downloader.available_models[model_id]
            status_icon = "✓" if is_downloaded else "✗"
            print(f"{status_icon} {model['name']}")

        print("=" * 70)
        return

    if args.recommended:
        downloader.download_recommended()
        return

    if args.model:
        downloader.download_model(args.model)
        return

    # No arguments, show help
    parser.print_help()


if __name__ == "__main__":
    main()
