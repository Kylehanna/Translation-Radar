# RAG Fixture Data

This directory holds local fixture inputs for the Translation Radar indexing pipeline.

Files:

- `normalized_records.json` contains normalized technology records that the default index build can ingest immediately.
- `feed_manifest.json` defines Inteum RSS feed harvest targets for the first harvester job.

Build the default normalized dataset from the Inteum RSS manifest with:

```bash
PYTHONPATH=src .venv/bin/python -m translation_radar_api.services.rag_harvest
```

Build the index snapshot with:

```bash
PYTHONPATH=src .venv/bin/python -c "from translation_radar_api.services.rag_search import build_seed_rag_index; print(build_seed_rag_index().model_dump())"
```