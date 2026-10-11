"""Pure shaping of Graphiti/FalkorDB query rows into the viewer's graph contract.

No external imports, so it is testable standalone. The contract the strix-fork
viewer expects (strix/interface/viewer/memory_graph.py):

    {"nodes": [{"id","label","type"}, ...],
     "edges": [{"source","target","label"}, ...]}
"""

from __future__ import annotations

from typing import Any


def rows_to_graph(
    edge_rows: list[tuple[Any, Any, Any, Any, Any, Any]],
    node_rows: list[tuple[Any, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Build the graph from two FalkorDB result sets.

    edge_rows: (src_uuid, src_name, dst_uuid, dst_name, rel_name, rel_fact)
    node_rows: (uuid, name)  — every Entity for the group, so isolated nodes show too
    """
    nodes: dict[str, dict[str, Any]] = {}

    def _add_node(uuid: Any, name: Any) -> str | None:
        if uuid is None:
            return None
        nid = str(uuid)
        if nid not in nodes:
            nodes[nid] = {"id": nid, "label": str(name or nid), "type": "entity"}
        return nid

    for uuid, name in node_rows:
        _add_node(uuid, name)

    edges: list[dict[str, Any]] = []
    for i, row in enumerate(edge_rows):
        src_uuid, src_name, dst_uuid, dst_name, rel_name, rel_fact = row
        s = _add_node(src_uuid, src_name)
        t = _add_node(dst_uuid, dst_name)
        if s is None or t is None:
            continue
        label = str(rel_name or rel_fact or "")
        edges.append({"id": f"e{i}", "source": s, "target": t, "label": label})

    return {"nodes": list(nodes.values()), "edges": edges}
