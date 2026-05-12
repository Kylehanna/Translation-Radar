from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class PublicationSignal(BaseModel):
    title: str
    abstract: str = ""
    published_on: date
    strategic_area: str
    citation_count: int = 0
    journal_impact_tier: str = "standard"


class GrantSignal(BaseModel):
    sponsor: str
    amount_usd: int = 0
    awarded_on: date
    translational: bool = False
    keywords: list[str] = Field(default_factory=list)


class DisclosureRecord(BaseModel):
    title: str
    disclosed_on: date
    strategic_area: str


class ResearcherRecord(BaseModel):
    researcher_id: str
    display_name: str
    department: str
    priority_score: float = 0.0
    publications: list[PublicationSignal] = Field(default_factory=list)
    grants: list[GrantSignal] = Field(default_factory=list)
    disclosures: list[DisclosureRecord] = Field(default_factory=list)


class AlertReason(BaseModel):
    code: str
    detail: str


class ScoutSignalAlert(BaseModel):
    researcher_id: str
    display_name: str
    department: str
    strategic_area: str
    alert_score: float
    recommendation: str
    reasons: list[AlertReason]


class ScoutSignalRequest(BaseModel):
    researchers: list[ResearcherRecord]
    minimum_score: float = 0.55


class ScoutSignalResponse(BaseModel):
    alerts: list[ScoutSignalAlert]


class SourceRecord(BaseModel):
    source_id: str
    institution_name: str
    source_type: str
    source_url: str
    title: str
    summary: str = ""
    contact_name: str | None = None
    contact_email: str | None = None
    category_tags: list[str] = Field(default_factory=list)
    posted_on: date | None = None
    raw_metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedTechnologyRecord(BaseModel):
    institution_name: str
    source_type: str
    source_url: str
    title: str
    summary: str
    contact_name: str | None = None
    contact_email: str | None = None
    category_tags: list[str] = Field(default_factory=list)
    posted_on: date | None = None
    raw_metadata: dict[str, Any] = Field(default_factory=dict)


class InteumRssNormalizationRequest(BaseModel):
    institution_name: str
    source_url: str
    feed_xml: str


class SourceNormalizationResponse(BaseModel):
    records: list[NormalizedTechnologyRecord]


class SourceRegistryEntry(BaseModel):
    institution_name: str
    host: str
    source_type: str
    status: str
    catalog_family: str = ""
    access_status: str = ""
    preferred_url: str = ""
    search_url: str = ""
    rss_url: str = ""
    parser_strategy: str = ""
    title_hint: str = ""
    notes: str = ""


class SourceRegistrySummary(BaseModel):
    registry_name: str
    observed_host_count: int
    rough_active_count_low: int
    rough_active_count_high: int
    entries: list[SourceRegistryEntry]


class SourceCatalogFamilyEntry(BaseModel):
    family_name: str
    source_type: str
    priority: int
    coverage_status: str
    parser_strategy: str
    example_urls: list[str] = Field(default_factory=list)
    detection_patterns: list[str] = Field(default_factory=list)
    notes: str = ""


class SourceCatalogFamilySummary(BaseModel):
    registry_name: str
    families: list[SourceCatalogFamilyEntry]


class InstitutionCoverageEntry(BaseModel):
    institution_name: str
    coverage_status: str
    matched_source_family: str = ""
    matched_source_type: str = ""
    matched_registry_institution: str = ""
    preferred_url: str = ""
    notes: list[str] = Field(default_factory=list)


class InstitutionCoverageSummary(BaseModel):
    coverage_name: str
    target_institution_count: int
    direct_coverage_count: int
    missing_direct_count: int
    canberra_retired: bool = False
    entries: list[InstitutionCoverageEntry] = Field(default_factory=list)


class CampusFamilyRegistryEntry(BaseModel):
    family_key: str
    family_name: str
    member_institution_name: str
    member_role: str
    source_type: str = ""
    preferred_url: str = ""
    search_url: str = ""
    coverage_status: str = ""
    notes: str = ""


class CampusFamilyRegistrySummary(BaseModel):
    registry_name: str
    family_count: int
    entries: list[CampusFamilyRegistryEntry] = Field(default_factory=list)


class OrganizationFamilyCoverageEntry(BaseModel):
    family_key: str
    family_name: str
    coverage_status: str
    target_member_count: int
    covered_member_count: int
    represented_institutions: list[str] = Field(default_factory=list)
    covered_institutions: list[str] = Field(default_factory=list)
    preferred_urls: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class OrganizationFamilyCoverageSummary(BaseModel):
    coverage_name: str
    target_family_count: int
    covered_family_count: int
    missing_family_count: int
    entries: list[OrganizationFamilyCoverageEntry] = Field(default_factory=list)


class PreferredCatalogRequest(BaseModel):
    institution_name: str
    aggregate_source_url: str | None = None
    aggregate_source_type: str = "aggregate"


class PreferredCatalogResponse(BaseModel):
    institution_name: str
    resolution_status: str
    preferred_entry: SourceRegistryEntry | None = None
    selected_url: str = ""
    selected_source_type: str = ""
    fallback_url: str = ""
    notes: list[str] = Field(default_factory=list)


class CatalogFetchAttempt(BaseModel):
    url: str
    source_type: str
    success: bool
    http_status: int | None = None
    final_url: str = ""
    title: str = ""
    error: str = ""


class PreferredCatalogFetchResponse(BaseModel):
    institution_name: str
    selected_url: str = ""
    selected_source_type: str = ""
    used_fallback: bool = False
    attempts: list[CatalogFetchAttempt] = Field(default_factory=list)


class RagSearchFilters(BaseModel):
    organization_names: list[str] = Field(default_factory=list)
    organization_types: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    direct_source_only: bool = False
    licensing_statuses: list[str] = Field(default_factory=list)


class RagSearchRequest(BaseModel):
    query: str
    filters: RagSearchFilters = Field(default_factory=RagSearchFilters)
    top_k: int = 10
    include_answer: bool = True


class RagEvidenceChunk(BaseModel):
    chunk_id: str
    text: str
    source_url: str


class RagTechnologyResult(BaseModel):
    technology_id: str
    title: str
    organization_name: str
    organization_type: str
    source_url: str
    catalog_family: str
    licensing_status: str
    score: float
    summary: str
    tags: list[str] = Field(default_factory=list)
    published_at: date | None = None
    evidence: list[RagEvidenceChunk] = Field(default_factory=list)


class RagAnswer(BaseModel):
    summary: str
    model: str = "heuristic-retrieval-v1"
    generated_at: date


class RagCoverageStatus(BaseModel):
    direct_covered_count: int
    target_count: int
    snapshot_record_count: int
    covered_family_count: int
    family_target_count: int


class RagSearchResponse(BaseModel):
    query: str
    answer: RagAnswer | None = None
    results: list[RagTechnologyResult] = Field(default_factory=list)
    coverage: RagCoverageStatus


class RagTechnologyDetail(BaseModel):
    technology_id: str
    title: str
    organization_name: str
    organization_type: str
    source_url: str
    catalog_family: str
    licensing_status: str
    summary: str
    full_text: str
    tags: list[str] = Field(default_factory=list)
    published_at: date | None = None
    evidence: list[RagEvidenceChunk] = Field(default_factory=list)


class RagIndexedDocument(BaseModel):
    technology_id: str
    title: str
    organization_name: str
    organization_type: str
    source_url: str
    catalog_family: str
    licensing_status: str
    summary: str
    full_text: str
    tags: list[str] = Field(default_factory=list)
    published_at: date | None = None
    direct_source: bool = True
    searchable_text: str
    tokens: list[str] = Field(default_factory=list)


class RagIndexSnapshot(BaseModel):
    version: str = "rag-seed-index-v1"
    built_at: datetime
    document_count: int
    documents: list[RagIndexedDocument] = Field(default_factory=list)


class RagIndexBuildResponse(BaseModel):
    status: str
    index_path: str
    document_count: int
    built_at: datetime


class RagIndexStatusResponse(BaseModel):
    exists: bool
    index_path: str
    document_count: int = 0
    built_at: datetime | None = None
    version: str = "rag-seed-index-v1"


class RagHarvestResponse(BaseModel):
    source_family: str
    manifest_path: str
    output_path: str
    record_count: int
    harvested_at: datetime