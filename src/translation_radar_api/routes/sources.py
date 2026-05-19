import csv
from io import StringIO

from fastapi import APIRouter, Response

from translation_radar_api.models import (
    CatalogFetchAttempt,
    InteumRssNormalizationRequest,
    InstitutionCoverageSummary,
    PreferredCatalogFetchResponse,
    PreferredCatalogRequest,
    PreferredCatalogResponse,
    SourceCatalogFamilySummary,
    SourceNormalizationResponse,
    SourceRegistrySummary,
)
from translation_radar_api.sources.http_probe import probe_url
from translation_radar_api.sources.registry import (
    load_autm_2018_coverage_summary,
    load_autm_2022_coverage_summary,
    load_campus_family_registry,
    load_catalog_family_registry,
    load_technology_publisher_registry,
    resolve_preferred_catalog,
)
from translation_radar_api.sources.inteum_rss import parse_inteum_rss_feed


router = APIRouter(prefix="/sources", tags=["sources"])


def build_csv_response(filename: str, fieldnames: list[str], rows: list[dict[str, str]]) -> Response:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def build_preferred_catalog_response(payload: PreferredCatalogRequest) -> PreferredCatalogResponse:
    preferred_entry, selected_url, selected_source_type, notes = resolve_preferred_catalog(
        institution_name=payload.institution_name,
        aggregate_source_url=payload.aggregate_source_url,
        aggregate_source_type=payload.aggregate_source_type,
    )
    resolution_status = "direct-match" if preferred_entry else ("fallback-only" if selected_url else "unresolved")
    return PreferredCatalogResponse(
        institution_name=payload.institution_name,
        resolution_status=resolution_status,
        preferred_entry=preferred_entry,
        selected_url=selected_url,
        selected_source_type=selected_source_type,
        fallback_url=payload.aggregate_source_url or "",
        notes=notes,
    )


def fetch_preferred_catalog_metadata(payload: PreferredCatalogRequest) -> PreferredCatalogFetchResponse:
    resolution = build_preferred_catalog_response(payload)
    attempts: list[CatalogFetchAttempt] = []

    if resolution.selected_url:
        result = probe_url(resolution.selected_url)
        attempts.append(
            CatalogFetchAttempt(
                url=resolution.selected_url,
                source_type=resolution.selected_source_type,
                success=result.success,
                http_status=result.http_status,
                final_url=result.final_url,
                title=result.title,
                error=result.error,
            )
        )
        if result.success:
            return PreferredCatalogFetchResponse(
                institution_name=payload.institution_name,
                selected_url=resolution.selected_url,
                selected_source_type=resolution.selected_source_type,
                used_fallback=False,
                attempts=attempts,
            )

    if payload.aggregate_source_url and payload.aggregate_source_url != resolution.selected_url:
        fallback_result = probe_url(payload.aggregate_source_url)
        attempts.append(
            CatalogFetchAttempt(
                url=payload.aggregate_source_url,
                source_type=payload.aggregate_source_type,
                success=fallback_result.success,
                http_status=fallback_result.http_status,
                final_url=fallback_result.final_url,
                title=fallback_result.title,
                error=fallback_result.error,
            )
        )
        if fallback_result.success:
            return PreferredCatalogFetchResponse(
                institution_name=payload.institution_name,
                selected_url=payload.aggregate_source_url,
                selected_source_type=payload.aggregate_source_type,
                used_fallback=True,
                attempts=attempts,
            )

    return PreferredCatalogFetchResponse(
        institution_name=payload.institution_name,
        selected_url="",
        selected_source_type="",
        used_fallback=False,
        attempts=attempts,
    )


@router.post("/normalize/inteum-rss", response_model=SourceNormalizationResponse)
def normalize_inteum_rss(payload: InteumRssNormalizationRequest) -> SourceNormalizationResponse:
    return SourceNormalizationResponse(
        records=parse_inteum_rss_feed(
            feed_xml=payload.feed_xml,
            institution_name=payload.institution_name,
            source_url=payload.source_url,
        )
    )


@router.post("/resolve/preferred-catalog", response_model=PreferredCatalogResponse)
def resolve_preferred_catalog_route(payload: PreferredCatalogRequest) -> PreferredCatalogResponse:
    return build_preferred_catalog_response(payload)


@router.post("/fetch/preferred-catalog", response_model=PreferredCatalogFetchResponse)
def fetch_preferred_catalog_route(payload: PreferredCatalogRequest) -> PreferredCatalogFetchResponse:
    return fetch_preferred_catalog_metadata(payload)


@router.get("/registry/technologypublisher", response_model=SourceRegistrySummary)
def technology_publisher_registry() -> SourceRegistrySummary:
    return load_technology_publisher_registry()


@router.get("/registry/technologypublisher.csv")
def technology_publisher_registry_csv() -> Response:
    summary = load_technology_publisher_registry()
    fieldnames = [
        "institution_name",
        "host",
        "source_type",
        "status",
        "catalog_family",
        "access_status",
        "preferred_url",
        "search_url",
        "rss_url",
        "parser_strategy",
        "title_hint",
        "notes",
    ]
    rows = [
        {
            "institution_name": entry.institution_name,
            "host": entry.host,
            "source_type": entry.source_type,
            "status": entry.status,
            "catalog_family": entry.catalog_family,
            "access_status": entry.access_status,
            "preferred_url": entry.preferred_url,
            "search_url": entry.search_url,
            "rss_url": entry.rss_url,
            "parser_strategy": entry.parser_strategy,
            "title_hint": entry.title_hint,
            "notes": entry.notes,
        }
        for entry in summary.entries
    ]
    return build_csv_response("technologypublisher_registry.csv", fieldnames, rows)


@router.get("/registry/campus-families.csv")
def campus_family_registry_csv() -> Response:
    summary = load_campus_family_registry()
    fieldnames = [
        "family_key",
        "family_name",
        "member_institution_name",
        "member_role",
        "source_type",
        "preferred_url",
        "search_url",
        "coverage_status",
        "notes",
    ]
    rows = [
        {
            "family_key": entry.family_key,
            "family_name": entry.family_name,
            "member_institution_name": entry.member_institution_name,
            "member_role": entry.member_role,
            "source_type": entry.source_type,
            "preferred_url": entry.preferred_url,
            "search_url": entry.search_url,
            "coverage_status": entry.coverage_status,
            "notes": entry.notes,
        }
        for entry in summary.entries
    ]
    return build_csv_response("campus_family_registry.csv", fieldnames, rows)


@router.get("/registry/catalog-families", response_model=SourceCatalogFamilySummary)
def catalog_family_registry() -> SourceCatalogFamilySummary:
    return load_catalog_family_registry()


@router.get("/registry/catalog-families.csv")
def catalog_family_registry_csv() -> Response:
    summary = load_catalog_family_registry()
    fieldnames = [
        "family_name",
        "source_type",
        "priority",
        "coverage_status",
        "parser_strategy",
        "example_urls",
        "detection_patterns",
        "notes",
    ]
    rows = [
        {
            "family_name": entry.family_name,
            "source_type": entry.source_type,
            "priority": str(entry.priority),
            "coverage_status": entry.coverage_status,
            "parser_strategy": entry.parser_strategy,
            "example_urls": " | ".join(entry.example_urls),
            "detection_patterns": " | ".join(entry.detection_patterns),
            "notes": entry.notes,
        }
        for entry in summary.families
    ]
    return build_csv_response("catalog_families.csv", fieldnames, rows)


@router.get("/coverage/autm-2022", response_model=InstitutionCoverageSummary)
def autm_2022_coverage() -> InstitutionCoverageSummary:
    return load_autm_2022_coverage_summary()


@router.get("/coverage/autm-2022.csv")
def autm_2022_coverage_csv() -> Response:
    summary = load_autm_2022_coverage_summary()
    fieldnames = [
        "institution_name",
        "coverage_status",
        "matched_source_family",
        "matched_source_type",
        "matched_registry_institution",
        "preferred_url",
        "notes",
    ]
    rows = [
        {
            "institution_name": entry.institution_name,
            "coverage_status": entry.coverage_status,
            "matched_source_family": entry.matched_source_family,
            "matched_source_type": entry.matched_source_type,
            "matched_registry_institution": entry.matched_registry_institution,
            "preferred_url": entry.preferred_url,
            "notes": " | ".join(entry.notes),
        }
        for entry in summary.entries
    ]
    return build_csv_response("autm_2022_coverage.csv", fieldnames, rows)


@router.get("/coverage/autm-2018", response_model=InstitutionCoverageSummary)
def autm_2018_coverage() -> InstitutionCoverageSummary:
    return load_autm_2018_coverage_summary()


@router.get("/coverage/autm-2018.csv")
def autm_2018_coverage_csv() -> Response:
    summary = load_autm_2018_coverage_summary()
    fieldnames = [
        "institution_name",
        "coverage_status",
        "matched_source_family",
        "matched_source_type",
        "matched_registry_institution",
        "preferred_url",
        "notes",
    ]
    rows = [
        {
            "institution_name": entry.institution_name,
            "coverage_status": entry.coverage_status,
            "matched_source_family": entry.matched_source_family,
            "matched_source_type": entry.matched_source_type,
            "matched_registry_institution": entry.matched_registry_institution,
            "preferred_url": entry.preferred_url,
            "notes": " | ".join(entry.notes),
        }
        for entry in summary.entries
    ]
    return build_csv_response("autm_2018_coverage.csv", fieldnames, rows)