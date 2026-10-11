"""MiroFish adapter blueprint (strix-fork items 11-12).

A Flask Blueprint you register inside your MiroFish app (`create_app`) to expose
the two endpoints the strix-fork client (strix/integrations/mirofish.py) calls:

    POST /personas  {"spec": {...}, "count": N}
      -> {"personas": [{"name","role","attributes"}, ...]}
    POST /rehearse  {"finding": {...}, "stakeholders": [...]?}
      -> {"reactions": [{"stakeholder","reaction","severity_felt"}, ...], "summary": ""}

The MiroFish calls are isolated in `_generate_personas` / `_rehearse` below and use
MiroFish's own services (OasisProfileGenerator, SimulationManager/Runner). Those
service signatures vary by MiroFish version; treat these two functions as the
wiring you confirm against your checkout (see README.md). The request parsing and
response shaping (shape.py) are version-independent and unit-tested.

LICENSE: AGPL-3.0. This file imports MiroFish (AGPL) and is a derivative work of
it; it is deliberately kept OUT of the Apache-2.0 strix-fork tree. See LICENSE.
"""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request

from shape import (
    BadRequest,
    parse_personas_request,
    parse_rehearse_request,
    shape_personas,
    shape_rehearsal,
)

strix_adapter = Blueprint("strix_adapter", __name__)


# --- MiroFish wiring (confirm against your MiroFish version) ----------------

def _generate_personas(spec: dict[str, Any], count: int) -> list[Any]:
    """Call MiroFish's persona generator for `count` entities described by `spec`.

    `spec` carries the entities/roles to model, e.g.
    {"entities": [{"name","type","description"}, ...]} or {"roles": [...]}.
    """
    from app.services.oasis_profile_generator import OasisProfileGenerator
    from app.services.zep_entity_reader import EntityNode  # MiroFish's entity type

    gen = OasisProfileGenerator(graph_id=spec.get("graph_id"))
    entities = spec.get("entities") or [{"name": r, "type": "role"} for r in spec.get("roles", [])]
    profiles: list[Any] = []
    for ent in entities[:count]:
        node = EntityNode(**ent) if not isinstance(ent, EntityNode) else ent
        profiles.append(gen.generate_profile_from_entity(node))
    return profiles


def _rehearse(finding: dict[str, Any], stakeholders: list[str]) -> tuple[list[Any], str]:
    """Seed a short MiroFish simulation with the finding and return per-stakeholder
    round summaries plus a one-line synthesis.

    This is the heavier, less-certain wiring: it drives MiroFish's simulation
    pipeline (create -> prepare -> run a few rounds) with the finding as the seed
    event and `stakeholders` as the agent groups. Adapt to your MiroFish sim API;
    see README.md. Until wired, it returns an empty rehearsal rather than faking
    reactions.
    """
    # Intentionally conservative: wire SimulationManager/Runner here for your
    # MiroFish version. Returning empty is honest when the pipeline isn't wired,
    # so the client never presents fabricated stakeholder reactions.
    _ = (finding, stakeholders)
    return [], ""


# --- HTTP endpoints (version-independent) -----------------------------------

@strix_adapter.post("/personas")
def personas():
    try:
        spec, count = parse_personas_request(request.get_json(silent=True) or {})
    except BadRequest as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(shape_personas(_generate_personas(spec, count)))


@strix_adapter.post("/rehearse")
def rehearse():
    try:
        finding, stakeholders = parse_rehearse_request(request.get_json(silent=True) or {})
    except BadRequest as exc:
        return jsonify({"error": str(exc)}), 400
    rounds, summary = _rehearse(finding, stakeholders)
    return jsonify(shape_rehearsal(rounds, summary))
