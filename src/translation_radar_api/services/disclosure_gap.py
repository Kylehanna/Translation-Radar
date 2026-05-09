from __future__ import annotations

from collections import Counter

from translation_radar_api.models import AlertReason, DisclosureGapResponse, GapAlert, ResearcherRecord


def score_researcher_gap(researcher: ResearcherRecord) -> GapAlert | None:
    if not researcher.publications:
        return None

    reasons: list[AlertReason] = []
    score = 0.0

    latest_publications = sorted(researcher.publications, key=lambda item: item.published_on, reverse=True)[:3]
    strategic_areas = [publication.strategic_area for publication in latest_publications]
    top_area = Counter(strategic_areas).most_common(1)[0][0]

    if len(researcher.disclosures) == 0:
        score += 0.35
        reasons.append(AlertReason(code="no_disclosures", detail="No linked disclosures found for this researcher."))

    recent_citations = sum(publication.citation_count for publication in latest_publications)
    if recent_citations >= 20:
        score += 0.15
        reasons.append(AlertReason(code="citation_velocity", detail="Recent publications show strong citation activity."))

    strategic_publication_count = sum(1 for publication in latest_publications if publication.strategic_area == top_area)
    if strategic_publication_count >= 2:
        score += 0.2
        reasons.append(
            AlertReason(
                code="strategic_cluster",
                detail=f"Multiple recent publications align to the strategic area '{top_area}'.",
            )
        )

    translational_grants = [grant for grant in researcher.grants if grant.translational or grant.amount_usd >= 500000]
    if translational_grants:
        score += 0.2
        reasons.append(AlertReason(code="grant_signal", detail="Recent grant activity suggests translational or scaled research momentum."))

    if researcher.priority_score >= 0.7:
        score += 0.1
        reasons.append(AlertReason(code="institution_priority", detail="Researcher is in a high-priority institutional segment."))

    if score < 0.35:
        return None

    if score >= 0.8:
        recommendation = "Engage now"
    elif score >= 0.6:
        recommendation = "Review with licensing manager"
    else:
        recommendation = "Monitor"

    return GapAlert(
        researcher_id=researcher.researcher_id,
        display_name=researcher.display_name,
        department=researcher.department,
        strategic_area=top_area,
        alert_score=round(min(score, 1.0), 2),
        recommendation=recommendation,
        reasons=reasons,
    )


def build_gap_alerts(researchers: list[ResearcherRecord], minimum_score: float = 0.55) -> DisclosureGapResponse:
    alerts = []
    for researcher in researchers:
        alert = score_researcher_gap(researcher)
        if alert and alert.alert_score >= minimum_score:
            alerts.append(alert)

    alerts.sort(key=lambda item: item.alert_score, reverse=True)
    return DisclosureGapResponse(alerts=alerts)