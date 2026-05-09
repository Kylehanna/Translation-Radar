from __future__ import annotations

from datetime import date

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


class GapAlert(BaseModel):
    researcher_id: str
    display_name: str
    department: str
    strategic_area: str
    alert_score: float
    recommendation: str
    reasons: list[AlertReason]


class DisclosureGapRequest(BaseModel):
    researchers: list[ResearcherRecord]
    minimum_score: float = 0.55


class DisclosureGapResponse(BaseModel):
    alerts: list[GapAlert]