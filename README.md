# Utilities Optimizer — steam & power

Finds the least-cost operation of an industrial steam and electricity system
(boilers, steam turbines, pressure headers, power purchase) and explains the decision.

**Status:** v0 — minimal model (2 boilers, back-pressure and condensing turbines, one HP/LP header pair).

## Roadmap

| Version | Content | Status |
|---|---|---|
| v0 | Minimal LP, electricity price break-even | in progress |
| v1 | Full HP/MP/LP site over one week, MILP (on/off, minimum load), balance tests | planned |
| v2 | Operating data in PostgreSQL, observed vs optimal operation, CUSUM | planned |
| v3 | API, small application, Docker, CI, price scenarios | planned |
| v4 | Steam demand forecast, rolling horizon | planned |

## Formulation

See [`docs/formulation.md`](docs/formulation.md).

## How to run

```bash
uv sync
uv run pytest -v
```

Data are synthetic. No confidential plant data is used.