from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, List, Optional

from .schema import Graph, Node, node_from_dict

try:
    from neo4j import GraphDatabase  # type: ignore[import]
except Exception:  # pragma: no cover - neo4j may not be installed
    GraphDatabase = None  # type: ignore[assignment]


@dataclass
class BibleManager:
    """
    High-level interface for working with the Bible graph.

    When the Neo4j driver is available and a connection succeeds, operations
    are executed against the database. Otherwise, an in-memory Graph is used
    as a graceful fallback so that the rest of the system can continue to
    function in environments without Neo4j.
    """

    _graph: Graph = field(default_factory=Graph, init=False)
    _driver: Any | None = field(default=None, init=False)

    # --- Connection management -------------------------------------------------

    def connect(self, uri: str, user: str, password: str) -> None:
        """
        Connect to a Neo4j instance if the driver is available.

        On failure (or if the driver is missing), the manager silently falls
        back to the in-memory Graph.
        """
        if GraphDatabase is None:
            self._driver = None
            return

        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            # Verify connectivity eagerly so we can fall back immediately.
            driver.verify_connectivity()
        except Exception:
            self._driver = None
            return

        self._driver = driver

    # --- Helper utilities ------------------------------------------------------

    def _use_memory(self) -> bool:
        return self._driver is None

    def _run_query(self, query: str, **params: Any) -> Iterable[Any]:
        """
        Run a Cypher query if a driver is available, falling back to no-op
        iteration on failure.
        """
        if self._driver is None:
            return []

        try:
            with self._driver.session() as session:
                result = session.run(query, **params)
                return list(result)
        except Exception:
            # If anything goes wrong, disable the driver and fall back.
            self._driver = None
            return []

    # --- Node operations -------------------------------------------------------

    def add_node(self, node: Node) -> None:
        """
        Add or update a node in the graph backend.
        """
        if self._use_memory():
            self._graph.add_node(node)
            return

        query = """
        MERGE (n:BibleNode {id: $id})
        SET n.type = $type,
            n.props = $props
        """
        self._run_query(query, id=node.id, type=node.type, props=node.props)

    def add_edge(self, from_id: str, rel: str, to_id: str) -> None:
        """
        Add an edge between two nodes.
        """
        if self._use_memory():
            self._graph.add_edge(from_id, rel, to_id)
            return

        query = """
        MATCH (a:BibleNode {id: $from_id})
        MATCH (b:BibleNode {id: $to_id})
        MERGE (a)-[r:BIBLE_RELATION {rel: $rel}]->(b)
        """
        self._run_query(query, from_id=from_id, to_id=to_id, rel=rel)

    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Retrieve a node by its ID.
        """
        if self._use_memory():
            return self._graph.get_node(node_id)

        query = """
        MATCH (n:BibleNode {id: $id})
        RETURN n.id AS id, n.type AS type, n.props AS props
        LIMIT 1
        """
        records = self._run_query(query, id=node_id)
        for record in records:
            data = {
                "id": record["id"],
                "type": record["type"],
                "props": record.get("props") or {},
            }
            return node_from_dict(data)
        return None

    def query_nodes_by_type(self, node_type: str) -> List[Node]:
        """
        Return all nodes whose type matches the given value.
        """
        if self._use_memory():
            return self._graph.find_nodes_by_type(node_type)

        query = """
        MATCH (n:BibleNode {type: $type})
        RETURN n.id AS id, n.type AS type, n.props AS props
        """
        records = self._run_query(query, type=node_type)
        results: List[Node] = []
        for record in records:
            data = {
                "id": record["id"],
                "type": record["type"],
                "props": record.get("props") or {},
            }
            results.append(node_from_dict(data))
        return results

    def query_neighbors(self, node_id: str, rel_type: Optional[str] = None) -> List[Node]:
        """
        Return neighbor nodes reachable from the given node via outgoing edges.

        If rel_type is provided, only edges with the given relation are
        considered.
        """
        if self._use_memory():
            return self._graph.query_neighbors(node_id, rel=rel_type)

        if rel_type is None:
            query = """
            MATCH (a:BibleNode {id: $id})-[:BIBLE_RELATION]->(b:BibleNode)
            RETURN b.id AS id, b.type AS type, b.props AS props
            """
            params = {"id": node_id}
        else:
            query = """
            MATCH (a:BibleNode {id: $id})-[r:BIBLE_RELATION {rel: $rel}]->(b:BibleNode)
            RETURN b.id AS id, b.type AS type, b.props AS props
            """
            params = {"id": node_id, "rel": rel_type}

        records = self._run_query(query, **params)
        neighbors: List[Node] = []
        for record in records:
            data = {
                "id": record["id"],
                "type": record["type"],
                "props": record.get("props") or {},
            }
            neighbors.append(node_from_dict(data))
        return neighbors

