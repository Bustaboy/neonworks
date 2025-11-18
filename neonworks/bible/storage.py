from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from .schema import Graph


PathLike = Union[str, Path]


def save_bible(graph: Graph, path: PathLike) -> None:
    """
    Persist a Graph representing the game bible to disk as JSON.
    """
    p = Path(path)
    if p.parent:
        p.parent.mkdir(parents=True, exist_ok=True)

    data = graph.to_dict()
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_bible(path: PathLike) -> Graph:
    """
    Load a Graph from a JSON file. If the file does not exist,
    return an empty Graph instance.
    """
    p = Path(path)
    if not p.exists():
        return Graph()

    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return Graph.from_dict(data)

