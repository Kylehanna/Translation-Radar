# Translation Radar

Translation Radar is a scout-facing translation intelligence platform for finding promising university and federal-lab technologies before they become obvious to the rest of the market.

The product is aimed at:
- corporate business development and technology scouting teams
- deep-tech and biotech investors
- strategic innovation teams tracking early commercialization signals

## Product Direction

The core workflow is:

1. Ingest technology listings, publications, patents, grants, translation funding, and institution metadata.
2. Normalize institutions, inventors, labs, and technology records into a common schema.
3. Enrich records with publication, funding, and patent context.
4. Rank opportunities against a scout thesis or market landscape.
5. Generate grounded briefs and evidence-backed scouting outputs.

## Core Use Cases

1. Scout agent
Given a thesis like "ADC linker platforms in US universities with translational funding," return ranked opportunities with source context.

2. Landscape agent
Map a technical area across institutions, funding, publications, and IP stage.

3. Outcome tracker
Watch which technologies later pick up SBIR funding, startup formation, licensing announcements, or public market milestones.

## First Build Slice

This repository starts with a minimal API and one deterministic agent:

- `Scout Signal Agent`

In the current codebase, this acts as the first ranking primitive for technology-scout intelligence. It compares publication and grant signals against disclosure history and emits explainable alerts with reasons and next-step recommendations.

## Repo Layout

```text
docs/
  ARCHITECTURE.md
src/
  translation_radar_api/
    main.py
    config.py
    models.py
    routes/
      alerts.py
      health.py
      sources.py
    services/
      scout_signal.py
    sources/
      base.py
      inteum_rss.py
tests/
  test_disclosure_gap.py
  test_inteum_rss.py
data/
  rag/
    normalized_records.json
    feed_manifest.json
  source_inventory/
    technologypublisher_hosts.csv
```

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn translation_radar_api.main:app --reload
```

Then open `http://127.0.0.1:8000/docs`.

## Near-Term Roadmap

1. Add source adapters for Inteum RSS, priority custom university sites, federal labs, OpenAlex, PubMed, and PatentsView.
2. Add a normalized persistence layer for institutions, researchers, technologies, publications, grants, patents, and alerts.
3. Add a thesis-driven scout endpoint that ranks opportunities against structured search criteria.
4. Add an evidence-backed opportunity brief endpoint for scout review.

## Current API Surfaces

- `POST /alerts/scout-signals` ranks researcher-linked scout signals
- `POST /sources/normalize/inteum-rss` normalizes Inteum-style RSS feeds into the common technology schema
- `GET /sources/registry/technologypublisher` returns the tracked Technology Publisher host inventory and rough active-count estimate
- `POST /rag/search` returns ranked technology matches from the current index snapshot or fallback seed corpus
- `POST /rag/index/build` writes the current RAG index snapshot
- `GET /rag/index/status` reports whether the current index snapshot exists

## Current RAG Build Flow

The current indexing slice works in three steps:

1. Harvest Inteum RSS feeds into `data/rag/normalized_records.json` with:

```bash
PYTHONPATH=src .venv/bin/python -m translation_radar_api.services.rag_harvest
```

2. Build the local index snapshot with:

```bash
PYTHONPATH=src .venv/bin/python -c "from translation_radar_api.services.rag_search import build_seed_rag_index; print(build_seed_rag_index().model_dump())"
```

3. Query the index through `POST /rag/search`.

The repository also ships a small set of real public normalized fixture records in `data/rag/normalized_records.json` so the default index build produces non-seed documents immediately.

For the live demo path, `data/rag/feed_manifest.json` is preloaded with public Technology Publisher RSS feeds for University of Pennsylvania, Emory University, George Washington University, University of Chicago, and University of South Alabama.
