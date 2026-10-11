# MiroFish adapter (strix-fork items 11-12)

A Flask **Blueprint** you register inside your MiroFish app to expose the two
endpoints the strix-fork client (`strix/integrations/mirofish.py`) calls:

```
POST /personas  {"spec": {...}, "count": N}
  -> {"personas": [{"name","role","attributes"}, ...]}
POST /rehearse  {"finding": {...}, "stakeholders": [...]?}
  -> {"reactions": [{"stakeholder","reaction","severity_felt"}, ...], "summary": ""}
```

> `shape.py` (request parsing + response shaping) is version-independent and
> tested. The MiroFish calls in `blueprint.py` (`_generate_personas`, `_rehearse`)
> are wiring you confirm against your MiroFish version — they are not verified
> against a running MiroFish here.

## License — AGPL-3.0 (important)

This adapter imports MiroFish, which is **AGPL-3.0**, so the adapter is a derivative
work and is **AGPL-3.0** too (see `LICENSE`). That is exactly why it lives here,
**outside** the Apache-2.0 strix-fork repo. Do not copy it into the fork. The fork's
Apache client only talks to it over HTTP; this adapter is part of *your* MiroFish
deployment and inherits MiroFish's license.

## How it plugs into MiroFish

Drop these two files (`blueprint.py`, `shape.py`) into your MiroFish backend
(e.g. `backend/app/strix_adapter/`) and register the blueprint in MiroFish's
`create_app` (`backend/app/__init__.py`), next to the existing blueprints:

```python
from app.strix_adapter.blueprint import strix_adapter
app.register_blueprint(strix_adapter, url_prefix="")   # serves /personas, /rehearse
```

Then point the fork at MiroFish:

```bash
export STRIX_MIROFISH_URL=http://127.0.0.1:5001
```

(MiroFish serves on 5001 in its compose; the fork's `deploy/mirofish.compose.yml`
publishes `127.0.0.1:5001`.)

## Wiring the two MiroFish calls

`blueprint.py` isolates the version-specific parts:

- **`_generate_personas(spec, count)`** — uses `OasisProfileGenerator(graph_id=...)`
  and `generate_profile_from_entity(node)` to turn `spec.entities` (or `spec.roles`)
  into persona profiles. Confirm `EntityNode`'s fields and the generator signature
  in your checkout (`backend/app/services/oasis_profile_generator.py`,
  `zep_entity_reader.py`).
- **`_rehearse(finding, stakeholders)`** — the heavier one. Seed a short simulation
  with the finding as the event and `stakeholders` as agent groups via
  `SimulationManager.create_simulation` / `prepare_simulation` and
  `SimulationRunner.start_simulation`, then map round summaries to reactions. It
  ships **conservative** (returns an empty rehearsal) so nothing fake is presented
  until you wire the real sim pipeline. Build it out against your MiroFish sim API.

## Safety

Personas are synthetic test users. Only seed them into applications you are
authorized to test.
