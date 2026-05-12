from __future__ import annotations

import json
from pathlib import Path
import re
from urllib.request import urlopen

from translation_radar_api.models import NormalizedTechnologyRecord, RagIndexedDocument
from translation_radar_api.sources.inteum_rss import parse_inteum_rss_feed
from translation_radar_api.sources.registry import resolve_preferred_catalog


def default_normalized_records_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "rag" / "normalized_records.json"


def default_feed_manifest_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "rag" / "feed_manifest.json"


def load_normalized_catalog_records(records_path: Path | None = None) -> list[NormalizedTechnologyRecord]:
    resolved_path = records_path or default_normalized_records_path()
    if not resolved_path.exists():
        return []

    payload = json.loads(resolved_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Normalized catalog record file must contain a JSON array.")

    return [NormalizedTechnologyRecord.model_validate(item) for item in payload]


def load_manifest_catalog_records(feed_manifest_path: Path | None = None) -> list[NormalizedTechnologyRecord]:
    resolved_path = feed_manifest_path or default_feed_manifest_path()
    if not resolved_path.exists():
        return []

    payload = json.loads(resolved_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Feed manifest file must contain a JSON array.")

    records: list[NormalizedTechnologyRecord] = []
    for item in payload:
        parser = item.get("parser", "inteum_rss")
        if parser != "inteum_rss":
            continue

        feed_xml = ""
        feed_path_value = item.get("feed_path")
        if feed_path_value:
            feed_path = Path(feed_path_value)
            if not feed_path.is_absolute():
                feed_path = resolved_path.parent / feed_path
            if not feed_path.exists():
                continue
            feed_xml = feed_path.read_text(encoding="utf-8")
        elif item.get("feed_url"):
            with urlopen(item["feed_url"], timeout=30) as response:  # noqa: S310 - manifest-controlled public source fetch
                feed_xml = response.read().decode("utf-8")
        else:
            continue

        records.extend(
            parse_inteum_rss_feed(
                feed_xml=feed_xml,
                institution_name=item["institution_name"],
                source_url=item["source_url"],
            )
        )

    return records


def load_catalog_records(
    records_path: Path | None = None,
    feed_manifest_path: Path | None = None,
) -> list[NormalizedTechnologyRecord]:
    if records_path is not None:
        normalized_records = load_normalized_catalog_records(records_path)
        if normalized_records:
            return normalized_records

    if feed_manifest_path is not None:
        return load_manifest_catalog_records(feed_manifest_path)

    normalized_records = load_normalized_catalog_records(records_path)
    if normalized_records:
        return normalized_records

    return load_manifest_catalog_records(feed_manifest_path)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "technology"


def _build_searchable_text(record: NormalizedTechnologyRecord) -> str:
    raw_values = [str(value) for value in record.raw_metadata.values() if isinstance(value, (str, int, float))]
    return " ".join(
        part
        for part in [record.title, record.summary, " ".join(record.category_tags), *raw_values]
        if part
    )


def _infer_licensing_status(record: NormalizedTechnologyRecord) -> str:
    raw_status = str(record.raw_metadata.get("ipStatus", "")).strip().lower()
    if "exclusive" in raw_status:
        return "exclusive-license"
    if raw_status:
        return raw_status.replace(" ", "-")
    return "available"


def _infer_technology_id(record: NormalizedTechnologyRecord) -> str:
    source_id = str(record.raw_metadata.get("guid") or record.raw_metadata.get("caseId") or "").strip()
    if source_id:
        return _slugify(f"{record.institution_name}-{source_id}")
    return _slugify(f"{record.institution_name}-{record.title}")


def normalized_record_to_index_document(record: NormalizedTechnologyRecord) -> RagIndexedDocument:
    preferred_entry, selected_url, selected_source_type, _ = resolve_preferred_catalog(
        institution_name=record.institution_name,
        aggregate_source_url=record.source_url,
        aggregate_source_type=record.source_type,
    )
    searchable_text = _build_searchable_text(record)
    return RagIndexedDocument(
        technology_id=_infer_technology_id(record),
        title=record.title,
        organization_name=record.institution_name,
        organization_type="institution",
        source_url=selected_url or record.source_url,
        catalog_family=preferred_entry.catalog_family if preferred_entry else "Normalized Catalog Records",
        licensing_status=_infer_licensing_status(record),
        summary=record.summary,
        full_text=searchable_text,
        tags=list(record.category_tags),
        published_at=record.posted_on,
        direct_source=True,
        searchable_text=searchable_text,
        tokens=[],
    )


def build_catalog_index_documents(
    records_path: Path | None = None,
    feed_manifest_path: Path | None = None,
) -> list[RagIndexedDocument]:
    return [
        normalized_record_to_index_document(record)
        for record in load_catalog_records(records_path=records_path, feed_manifest_path=feed_manifest_path)
    ]