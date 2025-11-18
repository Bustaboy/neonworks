from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, TypeVar


@dataclass
class Node:
    """
    Base graph node used by all specific Bible schema node types.
    """

    id: str
    type: str
    props: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the node into a JSON-serializable dictionary.
        """
        return {
            "id": self.id,
            "type": self.type,
            "props": self.props,
        }


@dataclass
class Character(Node):
    type: str = field(default="character", init=False)


@dataclass
class Location(Node):
    type: str = field(default="location", init=False)


@dataclass
class Quest(Node):
    type: str = field(default="quest", init=False)


@dataclass
class Item(Node):
    type: str = field(default="item", init=False)


@dataclass
class Mechanic(Node):
    type: str = field(default="mechanic", init=False)


@dataclass
class Faction(Node):
    type: str = field(default="faction", init=False)


@dataclass
class Asset(Node):
    type: str = field(default="asset", init=False)


@dataclass
class StyleGuide(Node):
    type: str = field(default="style_guide", init=False)


@dataclass
class GameplayRule(Node):
    type: str = field(default="gameplay_rule", init=False)


NODE_TYPE_REGISTRY: Dict[str, Type[Node]] = {
    "character": Character,
    "location": Location,
    "quest": Quest,
    "item": Item,
    "mechanic": Mechanic,
    "faction": Faction,
    "asset": Asset,
    "style_guide": StyleGuide,
    "gameplay_rule": GameplayRule,
}

N = TypeVar("N", bound=Node)


def node_from_dict(data: Dict[str, Any]) -> Node:
    """
    Factory to reconstruct a concrete Node subclass from its dictionary form.
    """
    node_type = data.get("type")
    node_cls = NODE_TYPE_REGISTRY.get(node_type, Node)
    return node_cls(
        id=data["id"],
        props=data.get("props", {}),
    )


@dataclass
class Edge:
    """
    Simple directional edge between two nodes.
    """

    from_id: str
    rel: str
    to_id: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "from": self.from_id,
            "rel": self.rel,
            "to": self.to_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Edge":
        return cls(
            from_id=data["from"],
            rel=data["rel"],
            to_id=data["to"],
        )


@dataclass
class Graph:
    """
    Lightweight, JSON-serializable graph for Bible content.
    """

    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)

    def add_node(self, node: Node) -> None:
        """
        Add or replace a node in the graph.
        """
        self.nodes[node.id] = node

    def add_edge(self, from_id: str, rel: str, to_id: str) -> None:
        """
        Add a directional edge between two nodes.

        Both endpoints must exist in the graph.
        """
        if from_id not in self.nodes:
            raise KeyError(f"Unknown from_id '{from_id}'")
        if to_id not in self.nodes:
            raise KeyError(f"Unknown to_id '{to_id}'")

        self.edges.append(Edge(from_id=from_id, rel=rel, to_id=to_id))

    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Retrieve a node by its ID.
        """
        return self.nodes.get(node_id)

    def find_nodes_by_type(self, node_type: str) -> List[Node]:
        """
        Return all nodes whose type matches the given value.
        """
        return [node for node in self.nodes.values() if node.type == node_type]

    def query_neighbors(self, node_id: str, rel: Optional[str] = None) -> List[Node]:
        """
        Return neighbor nodes reachable from the given node via outgoing edges.

        If rel is provided, only edges with the given relation are considered.
        """
        neighbors: List[Node] = []
        for edge in self.edges:
            if edge.from_id != node_id:
                continue
            if rel is not None and edge.rel != rel:
                continue
            neighbor = self.nodes.get(edge.to_id)
            if neighbor is not None:
                neighbors.append(neighbor)
        return neighbors

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the entire graph into a JSON-serializable dictionary.
        """
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Graph":
        """
        Reconstruct a Graph from its dictionary form.
        """
        graph = cls()
        for node_data in data.get("nodes", []):
            node = node_from_dict(node_data)
            graph.add_node(node)
        for edge_data in data.get("edges", []):
            edge = Edge.from_dict(edge_data)
            graph.add_edge(edge.from_id, edge.rel, edge.to_id)
        return graph

