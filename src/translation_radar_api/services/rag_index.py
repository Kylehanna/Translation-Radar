from __future__ import annotations

from pathlib import Path

from translation_radar_api.models import (
    RagIndexBuildResponse,
    RagIndexedDocument,
    RagIndexSnapshot,
    RagIndexStatusResponse,
)


def default_rag_index_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "rag" / "seed_index.json"


def write_rag_index_snapshot(
    documents: list[RagIndexedDocument],
    snapshot: RagIndexSnapshot,
    index_path: Path | None = None,
) -> RagIndexBuildResponse:
    resolved_path = index_path or default_rag_index_path()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(snapshot.model_dump_json(indent=2), encoding="utf-8")
    return RagIndexBuildResponse(
        status="built",
        index_path=str(resolved_path),
        document_count=len(documents),
        built_at=snapshot.built_at,
    )


def load_rag_index_snapshot(index_path: Path | None = None) -> RagIndexSnapshot | None:
    resolved_path = index_path or default_rag_index_path()
    if not resolved_path.exists():
        return None
    return RagIndexSnapshot.model_validate_json(resolved_path.read_text(encoding="utf-8"))


def get_rag_index_status(index_path: Path | None = None) -> RagIndexStatusResponse:
    resolved_path = index_path or default_rag_index_path()
    snapshot = load_rag_index_snapshot(resolved_path)
    if snapshot is None:
        return RagIndexStatusResponse(exists=False, index_path=str(resolved_path))
    return RagIndexStatusResponse(
        exists=True,
        index_path=str(resolved_path),
        document_count=snapshot.document_count,
        built_at=snapshot.built_at,
        version=snapshot.version,
    )