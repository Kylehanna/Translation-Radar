from datetime import date
import unittest

from translation_radar_api.models import DisclosureRecord, GrantSignal, PublicationSignal, ResearcherRecord
from translation_radar_api.services.disclosure_gap import build_gap_alerts


class DisclosureGapTests(unittest.TestCase):
    def test_scores_researcher_with_strong_gap_signals(self) -> None:
        researcher = ResearcherRecord(
            researcher_id="r-001",
            display_name="Dr. Maya Chen",
            department="Biomedical Engineering",
            priority_score=0.8,
            publications=[
                PublicationSignal(
                    title="Programmable cell circuits for precision therapeutics",
                    abstract="Synthetic biology for translational applications.",
                    published_on=date(2026, 4, 10),
                    strategic_area="biomanufacturing",
                    citation_count=16,
                    journal_impact_tier="high",
                ),
                PublicationSignal(
                    title="Scalable microbial chassis optimization",
                    published_on=date(2026, 3, 4),
                    strategic_area="biomanufacturing",
                    citation_count=8,
                ),
            ],
            grants=[
                GrantSignal(
                    sponsor="NIH",
                    amount_usd=750000,
                    awarded_on=date(2026, 1, 15),
                    translational=True,
                    keywords=["synthetic biology"],
                )
            ],
            disclosures=[],
        )

        response = build_gap_alerts([researcher], minimum_score=0.55)

        self.assertEqual(len(response.alerts), 1)
        self.assertEqual(response.alerts[0].recommendation, "Engage now")
        self.assertEqual(response.alerts[0].strategic_area, "biomanufacturing")

    def test_filters_low_signal_researcher(self) -> None:
        researcher = ResearcherRecord(
            researcher_id="r-002",
            display_name="Dr. Alex Stone",
            department="Chemistry",
            publications=[
                PublicationSignal(
                    title="Catalyst note",
                    published_on=date(2026, 4, 1),
                    strategic_area="materials",
                    citation_count=1,
                )
            ],
            grants=[],
            disclosures=[
                DisclosureRecord(
                    title="Catalyst platform",
                    disclosed_on=date(2025, 11, 2),
                    strategic_area="materials",
                )
            ],
        )

        response = build_gap_alerts([researcher], minimum_score=0.55)

        self.assertEqual(response.alerts, [])


if __name__ == "__main__":
    unittest.main()