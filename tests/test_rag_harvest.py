import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tests.test_inteum_rss import SAMPLE_FEED
from translation_radar_api.services.rag_harvest import harvest_inteum_rss_records


class RagHarvestTests(unittest.TestCase):
    def test_harvests_manifest_records_to_normalized_json(self) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "feed-manifest.json"
            output_path = temp_path / "normalized-records.json"

            manifest_path.write_text(
                json.dumps(
                    [
                        {
                            "institution_name": "Example University",
                            "source_url": "https://example.edu/tech/feed.xml",
                            "feed_url": "https://example.edu/tech/feed.xml",
                            "parser": "inteum_rss",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            response = harvest_inteum_rss_records(
                feed_manifest_path=manifest_path,
                output_path=output_path,
                fetch_text=lambda url: SAMPLE_FEED,
            )

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(response.record_count, 1)
            self.assertEqual(payload[0]["institution_name"], "Example University")
            self.assertEqual(payload[0]["title"], "Targeted ADC linker platform")


if __name__ == "__main__":
    unittest.main()