"""Memory-graph adapter: a thin REST shim in front of Graphiti's FalkorDB store.

Answers the contract the strix-fork viewer expects (its $STRIX_MEMORY_URL seam):

    GET /graph?group_id=<target>
      -> {"nodes": [{id,label,type}, ...], "edges": [{source,target,label}, ...]}
    GET /healthz -> {"ok": true}

It reads Graphiti's graph directly from FalkorDB (Graphiti stores :Entity nodes
joined by [:RELATES_TO] edges, both carrying group_id). This is a reference
implementation — verify the labels/props against your Graphiti version (see
README.md) before relying on it.

Licensed Apache-2.0 (Graphiti is Apache-2.0; this is original shim code).
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, request

from graph_shape import rows_to_graph

# Graphiti's FalkorDB schema (see README to adjust for your version).
_ENTITY_LABEL = os.environ.get("GRAPHITI_ENTITY_LABEL", "Entity")
_REL = os.environ.get("GRAPHITI_REL_TYPE", "RELATES_TO")

app = Flask(__name__)


def _graph():
    """Open the FalkorDB graph Graphiti writes to. Imported lazily so the pure
    shaping stays importable without the falkordb client installed."""
    from falkordb import FalkorDB

    db = FalkorDB(
        host=os.environ.get("FALKORDB_HOST", "memory"),
        port=int(os.environ.get("FALKORDB_PORT", "6379")),
        password=os.environ.get("FALKORDB_PASSWORD") or None,
    )
    return db.select_graph(os.environ.get("FALKORDB_DATABASE", "default_db"))


@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})


@app.get("/graph")
def graph():
    group_id = (request.args.get("group_id") or "").strip()
    if not group_id:
        return jsonify({"error": "group_id required"}), 400

    g = _graph()
    edge_q = (
        f"MATCH (s:{_ENTITY_LABEL} {{group_id:$gid}})-[e:{_REL} {{group_id:$gid}}]->"
        f"(t:{_ENTITY_LABEL} {{group_id:$gid}}) "
        "RETURN s.uuid, s.name, t.uuid, t.name, e.name, e.fact"
    )
    node_q = f"MATCH (n:{_ENTITY_LABEL} {{group_id:$gid}}) RETURN n.uuid, n.name"
    params = {"gid": group_id}
    edge_rows = [tuple(r) for r in g.query(edge_q, params).result_set]
    node_rows = [tuple(r) for r in g.query(node_q, params).result_set]
    return jsonify(rows_to_graph(edge_rows, node_rows))


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", "8070")))  # noqa: S104
