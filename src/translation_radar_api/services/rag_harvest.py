from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

from translation_radar_api.models import NormalizedTechnologyRecord, RagHarvestResponse
from translation_radar_api.services.rag_ingest import default_feed_manifest_path, default_normalized_records_path
from translation_radar_api.sources.inteum_rss import parse_inteum_rss_feed


def _default_fetch_text(url: str, timeout: int = 30) -> str:
    with urlopen(url, timeout=timeout) as response:  # noqa: S310 - manifest-controlled public source fetch
        return response.read().decode("utf-8")


def harvest_inteum_rss_records(
    feed_manifest_path: Path | None = None,
    output_path: Path | None = None,
    fetch_text: callable | None = None,
) -> RagHarvestResponse:
    resolved_manifest = feed_manifest_path or default_feed_manifest_path()
    resolved_output = output_path or default_normalized_records_path()
    fetcher = fetch_text or _default_fetch_text

    if not resolved_manifest.exists():
        raise FileNotFoundError(f"Feed manifest not found: {resolved_manifest}")

    payload = json.loads(resolved_manifest.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Feed manifest file must contain a JSON array.")

    records: list[NormalizedTechnologyRecord] = []
    for item in payload:
        if item.get("parser", "inteum_rss") != "inteum_rss":
            continue

        feed_xml = ""
        fixture_path = item.get("fixture_path", "")
        if fixture_path:
            resolved_fixture_path = Path(fixture_path)
            if not resolved_fixture_path.is_absolute():
                resolved_fixture_path = resolved_manifest.parent / resolved_fixture_path
            feed_xml = resolved_fixture_path.read_text(encoding="utf-8")
        elif item.get("feed_url"):
            feed_xml = fetcher(item["feed_url"])
        else:
            continue

        records.extend(
            parse_inteum_rss_feed(
                feed_xml=feed_xml,
                institution_name=item["institution_name"],
                source_url=item["source_url"],
            )
        )

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(
        json.dumps([record.model_dump(mode="json") for record in records], indent=2),
        encoding="utf-8",
    )

    return RagHarvestResponse(
        source_family="inteum_rss",
        manifest_path=str(resolved_manifest),
        output_path=str(resolved_output),
        record_count=len(records),
        harvested_at=datetime.now(timezone.utc),
    )


def main() -> None:
    response = harvest_inteum_rss_records()
    print(
        json.dumps(
            response.model_dump(mode="json"),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()