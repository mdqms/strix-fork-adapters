# Adapters

Reference adapters that fill the two live-service "seams" the strix-fork left
documented. They are kept here, **separate from the strix-fork repo**, on purpose:
one is AGPL (it derives from MiroFish) and must not live in the Apache-2.0 fork.

| Folder | Fills | License | Plugs into |
|---|---|---|---|
| `memory-graph-adapter/` | the viewer's `$STRIX_MEMORY_URL` seam (item 10) | Apache-2.0 | Graphiti's FalkorDB store |
| `mirofish-adapter/` | the `$STRIX_MIROFISH_URL` seam (items 11-12) | AGPL-3.0 | your MiroFish app |

Each folder has its own README with wiring instructions and what still needs
validating against a running service. In both, the pure data-shaping is unit-tested
here; the live calls into Graphiti / MiroFish are not (no running services in the
build env) and are the parts to verify when you wire them up.

These are not committed to the strix-fork git repo. Host or version them wherever
your deployment lives (the MiroFish one naturally belongs with your MiroFish
deployment under AGPL).
