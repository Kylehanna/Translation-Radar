import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json

from translation_radar_api.models import NormalizedTechnologyRecord, RagSearchFilters, RagSearchRequest
from translation_radar_api.services.rag_search import (
    build_rag_coverage_status,
    build_seed_rag_index,
    get_seed_technology_detail,
    get_seed_rag_index_status,
    search_seed_technology_records,
)
from tests.test_inteum_rss import SAMPLE_FEED


class RagSearchTests(unittest.TestCase):
    def test_search_returns_ranked_results(self) -> None:
        response = search_seed_technology_records(
            RagSearchRequest(query="oncology diagnostics", top_k=5)
        )

        self.assertEqual(response.query, "oncology diagnostics")
        self.assertTrue(response.results)
        self.assertEqual(response.results[0].organization_name, "Icahn School of Medicine at Mount Sinai")
        self.assertIn("direct-source evidence", response.answer.summary)

    def test_search_applies_filters(self) -> None:
        response = search_seed_technology_records(
            RagSearchRequest(
                query="oncology",
                filters=RagSearchFilters(organization_names=["H. Lee Moffitt Cancer Center & Research Institute"]),
            )
        )

        self.assertEqual(len(response.results), 1)
        self.assertEqual(response.results[0].organization_name, "H. Lee Moffitt Cancer Center & Research Institute")

    def test_returns_detail_for_seed_record(self) -> None:
        detail = get_seed_technology_detail("utep-memristor-actuators")

        self.assertIsNotNone(detail)
        self.assertEqual(detail.organization_name, "University of Texas at El Paso")
        self.assertEqual(detail.catalog_family, "TradeSpace Market")

    def test_builds_coverage_status(self) -> None:
        coverage = build_rag_coverage_status()

        self.assertEqual(coverage.direct_covered_count, 63)
        self.assertEqual(coverage.target_count, 237)
        self.assertEqual(coverage.snapshot_record_count, 5)

    def test_builds_index_snapshot(self) -> None:
        with TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "rag-index.json"

            build_response = build_seed_rag_index(index_path)
            status = get_seed_rag_index_status(index_path)

            self.assertEqual(build_response.status, "built")
            self.assertTrue(index_path.exists())
            self.assertTrue(status.exists)
            self.assertEqual(status.document_count, build_response.document_count)
            self.assertGreaterEqual(status.document_count, 5)

    def test_search_can_use_built_index_snapshot(self) -> None:
        with TemporaryDirectory() as temp_dir:
            index_path = Path(temp_dir) / "rag-index.json"
            build_seed_rag_index(index_path)

            response = search_seed_technology_records(
                RagSearchRequest(query="oncology diagnostics", top_k=5),
                index_path=index_path,
            )

            self.assertTrue(response.results)
            self.assertEqual(response.results[0].organization_name, "Icahn School of Medicine at Mount Sinai")

    def test_builds_index_from_normalized_catalog_records(self) -> None:
        with TemporaryDirectory() as temp_dir:
            records_path = Path(temp_dir) / "normalized-records.json"
            index_path = Path(temp_dir) / "rag-index.json"
            records_path.write_text(
                json.dumps(
                    [
                        NormalizedTechnologyRecord(
                            institution_name="University of Cincinnati",
                            source_type="inteum_rss",
                            source_url="https://uc.example.edu/rss",
                            title="Nanoparticle imaging agent",
                            summary="Molecular imaging platform for oncology diagnostics.",
                            category_tags=["oncology", "diagnostics"],
                            raw_metadata={"guid": "uc-tech-001", "ipStatus": "available"},
                        ).model_dump(mode="json")
                    ]
                ),
                encoding="utf-8",
            )

            build_response = build_seed_rag_index(index_path=index_path, normalized_records_path=records_path)
            response = search_seed_technology_records(
                RagSearchRequest(query="nanoparticle molecular imaging", top_k=5),
                index_path=index_path,
            )

            self.assertEqual(build_response.status, "built")
            self.assertEqual(response.results[0].organization_name, "University of Cincinnati")
            self.assertEqual(response.results[0].catalog_family, "Technology Publisher")

    def test_builds_index_from_feed_manifest_records(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            feed_path = temp_path / "sample-feed.xml"
            manifest_path = temp_path / "feed-manifest.json"
            index_path = temp_path / "rag-index.json"

            feed_path.write_text(SAMPLE_FEED, encoding="utf-8")
            manifest_path.write_text(
                json.dumps(
                    [
                        {
                            "institution_name": "Example University",
                            "source_url": "https://example.edu/tech/feed.xml",
                            "feed_path": str(feed_path),
                            "parser": "inteum_rss",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            build_seed_rag_index(index_path=index_path, feed_manifest_path=manifest_path)
            response = search_seed_technology_records(
                RagSearchRequest(query="linker chemistry antibody-drug conjugates", top_k=5),
                index_path=index_path,
            )

            self.assertEqual(response.results[0].organization_name, "Example University")
            self.assertEqual(response.results[0].title, "Targeted ADC linker platform")
