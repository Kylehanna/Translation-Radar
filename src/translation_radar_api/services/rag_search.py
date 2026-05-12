from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import log
from pathlib import Path
from datetime import datetime, timezone

from translation_radar_api.models import (
    RagAnswer,
    RagCoverageStatus,
    RagEvidenceChunk,
    RagIndexedDocument,
    RagIndexBuildResponse,
    RagIndexSnapshot,
    RagIndexStatusResponse,
    RagSearchFilters,
    RagSearchRequest,
    RagSearchResponse,
    RagTechnologyDetail,
    RagTechnologyResult,
)
from translation_radar_api.services.rag_index import (
    get_rag_index_status,
    load_rag_index_snapshot,
    write_rag_index_snapshot,
)
from translation_radar_api.services.rag_ingest import build_catalog_index_documents
from translation_radar_api.sources.registry import (
    load_autm_combined_coverage_summary,
    load_autm_combined_family_coverage_summary,
)


@dataclass(frozen=True)
class SeedTechnologyRecord:
    technology_id: str
    title: str
    organization_name: str
    organization_type: str
    source_url: str
    catalog_family: str
    licensing_status: str
    summary: str
    full_text: str
    tags: tuple[str, ...]
    published_at: date | None
    direct_source: bool = True


_SEED_TECHNOLOGY_RECORDS: tuple[SeedTechnologyRecord, ...] = (
    SeedTechnologyRecord(
        technology_id="usc-2024-170",
        title="Deterministic Benchmarking for Scalable Quantum Gate Calibration",
        organization_name="University of Southern California",
        organization_type="university",
        source_url="https://usc.technologypublisher.com/tech?title=2024-170_-_Deterministic_Benchmarking%3a_fast_and_scalable_calibration_of_qubit_logic_gates_to_minimize_downtime",
        catalog_family="Technology Publisher",
        licensing_status="available",
        summary="Quantum benchmarking workflow designed to reduce calibration downtime and improve fault-tolerant quantum system performance.",
        full_text="USC researchers developed a deterministic benchmarking workflow for calibrating qubit logic gates with lower downtime. The technology is positioned for quantum computing, calibration tooling, and research infrastructure commercialization.",
        tags=("quantum", "calibration", "software"),
        published_at=date(2026, 4, 30),
    ),
    SeedTechnologyRecord(
        technology_id="moffitt-9885",
        title="Bax Fragment Induced Tumor Cell Death",
        organization_name="H. Lee Moffitt Cancer Center & Research Institute",
        organization_type="cancer_center",
        source_url="http://moffitt.technologypublisher.com/technology/9885",
        catalog_family="Technology Publisher",
        licensing_status="available",
        summary="Oncology therapeutic approach centered on Bax fragment induced tumor cell death for cancer treatment strategies.",
        full_text="Moffitt lists a technology focused on Bax fragment induced tumor cell death. The opportunity fits oncology therapeutics and translational cancer licensing use cases.",
        tags=("oncology", "therapeutics", "cancer"),
        published_at=date(2012, 7, 30),
    ),
    SeedTechnologyRecord(
        technology_id="utep-memristor-actuators",
        title="Coupled Memristor Devices for Feedback Control and Sensing of Micro and Nanoelectromechanical Actuators",
        organization_name="University of Texas at El Paso",
        organization_type="university",
        source_url="https://utep.tradespacemarket.com/opportunities/0df5a9006a4ecf2d57c1e3f1e",
        catalog_family="TradeSpace Market",
        licensing_status="exclusive-license",
        summary="Advanced sensing and control technology for micro and nanoelectromechanical devices with licensing availability through UTEP's marketplace.",
        full_text="UTEP publishes a TradeSpace opportunity for coupled memristor devices enabling feedback control and sensing of micro and nanoelectromechanical actuators and sensors. Availability includes exclusive and non-exclusive licensing.",
        tags=("sensors", "hardware", "memristor"),
        published_at=None,
    ),
    SeedTechnologyRecord(
        technology_id="stanford-techfinder-cardiology-ai",
        title="AI Model for Cardiology Imaging Triage",
        organization_name="Stanford University",
        organization_type="university",
        source_url="https://techfinder.stanford.edu/",
        catalog_family="Custom University Catalogs",
        licensing_status="available",
        summary="Clinical decision support model for cardiology imaging triage and prioritization in hospital workflows.",
        full_text="Stanford technology catalog includes AI-enabled healthcare software opportunities relevant to imaging triage, clinical workflow optimization, and provider decision support.",
        tags=("ai", "medical imaging", "clinical decision support"),
        published_at=None,
    ),
    SeedTechnologyRecord(
        technology_id="mount-sinai-precision-oncology",
        title="Precision Oncology Biomarker Platform",
        organization_name="Icahn School of Medicine at Mount Sinai",
        organization_type="medical_school",
        source_url="https://ip.mountsinai.org/technologies/",
        catalog_family="Custom University Catalogs",
        licensing_status="available",
        summary="Biomarker platform aimed at oncology stratification, translational diagnostics, and precision medicine commercialization.",
        full_text="Mount Sinai Innovation Partners publishes technologies spanning biomarkers, diagnostics, and translational medicine. This seeded record represents precision oncology biomarker discovery and commercialization.",
        tags=("oncology", "diagnostics", "biomarker"),
        published_at=None,
    ),
)


def _tokenize(value: str) -> set[str]:
    return {token for token in "".join(char.lower() if char.isalnum() else " " for char in value).split() if token}


def _matches_filters(record: SeedTechnologyRecord, filters: RagSearchFilters) -> bool:
    if filters.organization_names and record.organization_name not in filters.organization_names:
        return False
    if filters.organization_types and record.organization_type not in filters.organization_types:
        return False
    if filters.categories and not set(filters.categories).intersection(record.tags):
        return False
    if filters.licensing_statuses and record.licensing_status not in filters.licensing_statuses:
        return False
    if filters.direct_source_only and not record.direct_source:
        return False
    return True


def _to_index_document(record: SeedTechnologyRecord) -> RagIndexedDocument:
    searchable_text = " ".join((record.title, record.summary, record.full_text, " ".join(record.tags)))
    return RagIndexedDocument(
        technology_id=record.technology_id,
        title=record.title,
        organization_name=record.organization_name,
        organization_type=record.organization_type,
        source_url=record.source_url,
        catalog_family=record.catalog_family,
        licensing_status=record.licensing_status,
        summary=record.summary,
        full_text=record.full_text,
        tags=list(record.tags),
        published_at=record.published_at,
        direct_source=record.direct_source,
        searchable_text=searchable_text,
        tokens=sorted(_tokenize(searchable_text)),
    )


def _seed_index_documents() -> list[RagIndexedDocument]:
    return [_to_index_document(record) for record in _SEED_TECHNOLOGY_RECORDS]


def _dedupe_documents(documents: list[RagIndexedDocument]) -> list[RagIndexedDocument]:
    deduped: dict[str, RagIndexedDocument] = {}
    for document in documents:
        deduped.setdefault(document.technology_id, document)
    return list(deduped.values())


def _matches_index_filters(document: RagIndexedDocument, filters: RagSearchFilters) -> bool:
    if filters.organization_names and document.organization_name not in filters.organization_names:
        return False
    if filters.organization_types and document.organization_type not in filters.organization_types:
        return False
    if filters.categories and not set(filters.categories).intersection(document.tags):
        return False
    if filters.licensing_statuses and document.licensing_status not in filters.licensing_statuses:
        return False
    if filters.direct_source_only and not document.direct_source:
        return False
    return True


def _score_document(query_tokens: set[str], document: RagIndexedDocument) -> float:
    haystack = set(document.tokens) if document.tokens else _tokenize(document.searchable_text)
    overlap = query_tokens.intersection(haystack)
    if not overlap:
        return 0.0
    return round(len(overlap) * log(len(haystack) + 1, 10), 4)


def _load_index_documents(index_path: Path | None = None) -> list[RagIndexedDocument]:
    snapshot = load_rag_index_snapshot(index_path)
    if snapshot is not None:
        return snapshot.documents
    return _seed_index_documents()


def build_rag_coverage_status() -> RagCoverageStatus:
    combined = load_autm_combined_coverage_summary()
    family = load_autm_combined_family_coverage_summary()
    return RagCoverageStatus(
        direct_covered_count=combined.direct_coverage_count,
        target_count=combined.target_institution_count,
        snapshot_record_count=len(_SEED_TECHNOLOGY_RECORDS),
        covered_family_count=family.covered_family_count,
        family_target_count=family.target_family_count,
    )


def _to_result(document: RagIndexedDocument, score: float) -> RagTechnologyResult:
    return RagTechnologyResult(
        technology_id=document.technology_id,
        title=document.title,
        organization_name=document.organization_name,
        organization_type=document.organization_type,
        source_url=document.source_url,
        catalog_family=document.catalog_family,
        licensing_status=document.licensing_status,
        score=score,
        summary=document.summary,
        tags=list(document.tags),
        published_at=document.published_at,
        evidence=[
            RagEvidenceChunk(
                chunk_id=f"{document.technology_id}-evidence-1",
                text=document.full_text,
                source_url=document.source_url,
            )
        ],
    )


def build_seed_rag_index(
    index_path: Path | None = None,
    normalized_records_path: Path | None = None,
    feed_manifest_path: Path | None = None,
) -> RagIndexBuildResponse:
    catalog_documents = build_catalog_index_documents(
        records_path=normalized_records_path,
        feed_manifest_path=feed_manifest_path,
    )
    documents = _dedupe_documents([*catalog_documents, *_seed_index_documents()])
    documents = [document.model_copy(update={"tokens": sorted(_tokenize(document.searchable_text))}) for document in documents]
    snapshot = RagIndexSnapshot(
        built_at=datetime.now(timezone.utc),
        document_count=len(documents),
        documents=documents,
    )
    return write_rag_index_snapshot(documents, snapshot, index_path=index_path)


def get_seed_rag_index_status(index_path: Path | None = None) -> RagIndexStatusResponse:
    return get_rag_index_status(index_path)


def search_seed_technology_records(payload: RagSearchRequest, index_path: Path | None = None) -> RagSearchResponse:
    query_tokens = _tokenize(payload.query)
    scored_results = []
    for document in _load_index_documents(index_path):
        if not _matches_index_filters(document, payload.filters):
            continue
        score = _score_document(query_tokens, document)
        if score <= 0:
            continue
        scored_results.append((score, document))

    scored_results.sort(key=lambda item: item[0], reverse=True)
    top_results = [_to_result(document, score) for score, document in scored_results[: payload.top_k]]

    answer = None
    if payload.include_answer:
        if top_results:
            org_names = sorted({result.organization_name for result in top_results})
            answer = RagAnswer(
                summary=(
                    f"Found {len(top_results)} seeded technology matches for '{payload.query}' across "
                    f"{', '.join(org_names)}. Results are ranked with lightweight keyword overlap and include direct-source evidence."
                ),
                generated_at=date.today(),
            )
        else:
            answer = RagAnswer(
                summary=(
                    f"No seeded technology records matched '{payload.query}'. Adjust filters or ingest more catalog records before relying on RAG retrieval."
                ),
                generated_at=date.today(),
            )

    return RagSearchResponse(
        query=payload.query,
        answer=answer,
        results=top_results,
        coverage=build_rag_coverage_status(),
    )


def get_seed_technology_detail(technology_id: str) -> RagTechnologyDetail | None:
    for document in _load_index_documents():
        if document.technology_id != technology_id:
            continue
        return RagTechnologyDetail(
            technology_id=document.technology_id,
            title=document.title,
            organization_name=document.organization_name,
            organization_type=document.organization_type,
            source_url=document.source_url,
            catalog_family=document.catalog_family,
            licensing_status=document.licensing_status,
            summary=document.summary,
            full_text=document.full_text,
            tags=list(document.tags),
            published_at=document.published_at,
            evidence=[
                RagEvidenceChunk(
                    chunk_id=f"{document.technology_id}-evidence-1",
                    text=document.full_text,
                    source_url=document.source_url,
                )
            ],
        )
    return None