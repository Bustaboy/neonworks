from __future__ import annotations

import json
from typing import Any, Dict, List


def transcript_to_bible_ops(transcript: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Convert a mini JSON-like transcript into bible graph operations.

    This is a stub implementation intended to be replaced by an LLM-powered
    transformer later. For now, it expects the transcript to be either:

    - A JSON object with optional "nodes" and "edges" lists.
    - A JSON list of nodes, in which case edges defaults to an empty list.

    Any parsing failures result in an empty set of operations.
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    try:
        data = json.loads(transcript)
    except json.JSONDecodeError:
        return {"nodes": nodes, "edges": edges}

    if isinstance(data, dict):
        raw_nodes = data.get("nodes", [])
        raw_edges = data.get("edges", [])
        if isinstance(raw_nodes, list):
            nodes = [n for n in raw_nodes if isinstance(n, dict)]
        if isinstance(raw_edges, list):
            edges = [e for e in raw_edges if isinstance(e, dict)]
    elif isinstance(data, list):
        nodes = [n for n in data if isinstance(n, dict)]

    return {"nodes": nodes, "edges": edges}

