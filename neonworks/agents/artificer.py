from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union


PathLike = Union[str, Path]


def _generate_tags_placeholder(file_path: Path) -> List[str]:
    """
    Placeholder hook for future AI-driven tag generation.

    For now this returns an empty list so the index structure is stable
    and callers can rely on the presence of a tags field.
    """
    # TODO: Use an LLM backend to infer tags from filename / context.
    return []


@dataclass
class Artificer:
    """
    Builds and manages an index of asset files on disk.

    The Artificer is intentionally lightweight and deterministic for now:
    it scans a root directory for `.png` and `.ogg` files and records
    basic metadata (filename, relative path, and an empty list of tags).
    Tag generation will be delegated to AI models in a future iteration.
    """

    def build_asset_index(self, assets_root: Path) -> Dict[str, Any]:
        """
        Scan `assets_root` for supported asset files and return an index.

        The returned dict is JSON-serializable and has the form:
            {
              "root": "<absolute root path>",
              "assets": [
                {"filename": "...", "path": "relative/path.png", "tags": []},
                ...
              ],
            }
        """
        root = assets_root.resolve()
        assets: List[Dict[str, Any]] = []

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue

            suffix = file_path.suffix.lower()
            if suffix not in {".png", ".ogg"}:
                continue

            rel_path = file_path.relative_to(root)
            asset_entry = {
                "filename": file_path.name,
                "path": str(rel_path).replace("\\", "/"),
                "tags": _generate_tags_placeholder(file_path),
            }
            assets.append(asset_entry)

        # Sort deterministically by path for stable outputs.
        assets.sort(key=lambda a: a["path"])

        return {
            "root": str(root),
            "assets": assets,
        }

    def save_asset_index(self, index: Dict[str, Any], path: PathLike) -> None:
        """
        Persist an asset index to disk as JSON.
        """
        p = Path(path)
        if p.parent:
            p.parent.mkdir(parents=True, exist_ok=True)

        with p.open("w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def load_asset_index(self, path: PathLike) -> Dict[str, Any]:
        """
        Load an asset index from JSON. If the file does not exist,
        return an empty index structure.
        """
        p = Path(path)
        if not p.exists():
            return {"root": "", "assets": []}

        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Basic shape normalization to guard against missing keys.
        root = data.get("root", "")
        assets = data.get("assets", [])
        if not isinstance(assets, list):
            assets = []

        return {"root": root, "assets": assets}

