# Memory-graph adapter (Graphiti → viewer)

A tiny REST shim that fills the strix-fork viewer's `$STRIX_MEMORY_URL` seam. The
viewer's memory-graph view (`strix/interface/viewer/memory_graph.py`) fetches
`GET /graph?group_id=<target>` and expects:

```json
{"nodes": [{"id","label","type"}, ...], "edges": [{"source","target","label"}, ...]}
```

Graphiti itself is retrieval-oriented and has no "dump a group's graph" call, so
this shim reads the graph **directly from FalkorDB**, where Graphiti stores
`:Entity` nodes joined by `[:RELATES_TO]` edges (both carrying `group_id`).

> Reference implementation. The pure shaping (`graph_shape.py`) is tested, but the
> live FalkorDB query is not verified against a running Graphiti here — confirm the
> labels/properties below match your Graphiti version first.

## How it plugs into Graphiti

It talks to the **same FalkorDB** the Graphiti MCP memory service uses (the
`memory` service in `strix-fork/deploy/docker-compose.yml`). It does not call
Graphiti; it reads its store. Run this shim on the stack's internal network and
point the viewer at it:

```bash
pip install -r requirements.txt
export FALKORDB_HOST=memory FALKORDB_PORT=6379 FALKORDB_DATABASE=default_db
# (FALKORDB_PASSWORD if you set one)
python adapter.py            # serves on :8070
# then, for host Strix's viewer:
export STRIX_MEMORY_URL=http://127.0.0.1:8070
```

Or add it to the deploy stack as its own service on `strix-fork_strixnet`, publishing
`127.0.0.1:8070` only (same posture as the rest of the stack).

## Schema knobs (adjust to your Graphiti version)

Graphiti's labels have been stable, but if a version differs, override via env:

| Env | Default | Meaning |
|---|---|---|
| `GRAPHITI_ENTITY_LABEL` | `Entity` | node label for entities |
| `GRAPHITI_REL_TYPE` | `RELATES_TO` | entity-to-entity edge type |
| `FALKORDB_DATABASE` | `default_db` | the FalkorDB graph key Graphiti writes to |

The query returned per edge is `(s.uuid, s.name, t.uuid, t.name, e.name, e.fact)`
and per node `(n.uuid, n.name)`; node id = `uuid`, label = `name`, edge label =
the relation `name` (falling back to `fact`). If your Graphiti stores the human
relation text only in `fact`, that is what shows on edges.

## Verify after wiring

1. Run a scan so the agent writes memory for a target (group_id = the target key).
2. `curl "http://127.0.0.1:8070/graph?group_id=<target>"` — expect non-empty nodes.
3. Open that run in `strix view`; the "Target memory graph" panel should render it.

If nodes come back empty but memory exists, your Graphiti labels differ — set the
env knobs above.
