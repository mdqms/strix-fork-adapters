"""Pure request parsing / response shaping for the MiroFish adapter.

No MiroFish or Flask imports, so it is testable standalone. Keeps the HTTP
contract (strix/integrations/mirofish.py) separate from the MiroFish calls, which
live in blueprint.py.
"""

from __future__ import annotations

from typing import Any


class BadRequest(ValueError):
    """Malformed request body."""


def parse_personas_request(body: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """Return (spec, count) from a /personas body, validated."""
    if not isinstance(body, dict):
        raise BadRequest("body must be an object")
    spec = body.get("spec")
    if not isinstance(spec, dict):
        raise BadRequest("'spec' object required")
    count = body.get("count", 10)
    if not isinstance(count, int) or count < 1 or count > 200:
        raise BadRequest("'count' must be an int in 1..200")
    return spec, count


def parse_rehearse_request(body: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Return (finding, stakeholders) from a /rehearse body, validated."""
    if not isinstance(body, dict):
        raise BadRequest("body must be an object")
    finding = body.get("finding")
    if not isinstance(finding, dict) or not finding:
        raise BadRequest("'finding' object required")
    stakeholders = body.get("stakeholders") or ["customers", "press", "regulators", "engineers"]
    if not isinstance(stakeholders, list) or not all(isinstance(s, str) for s in stakeholders):
        raise BadRequest("'stakeholders' must be a list of strings")
    return finding, stakeholders


def shape_personas(profiles: list[Any]) -> dict[str, Any]:
    """Shape MiroFish OasisAgentProfile objects (or dicts) into the client contract."""
    out: list[dict[str, Any]] = []
    for p in profiles:
        d = p.to_dict() if hasattr(p, "to_dict") else (p if isinstance(p, dict) else None)
        if not isinstance(d, dict):
            continue
        out.append(
            {
                "name": str(d.get("user_name") or d.get("name") or d.get("realname") or ""),
                "role": str(d.get("role") or d.get("occupation") or d.get("persona") or ""),
                "attributes": d,
            }
        )
    return {"personas": out}


def shape_rehearsal(round_summaries: list[Any], summary: str = "") -> dict[str, Any]:
    """Shape MiroFish round summaries into stakeholder reactions."""
    reactions: list[dict[str, Any]] = []
    for r in round_summaries:
        d = r if isinstance(r, dict) else getattr(r, "__dict__", {})
        reactions.append(
            {
                "stakeholder": str(d.get("stakeholder") or d.get("persona") or d.get("group") or "?"),
                "reaction": str(d.get("summary") or d.get("reaction") or d.get("text") or ""),
                "severity_felt": str(d.get("sentiment") or d.get("severity_felt") or ""),
            }
        )
    return {"reactions": reactions, "summary": summary}
