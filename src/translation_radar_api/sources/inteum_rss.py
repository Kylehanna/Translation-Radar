from __future__ import annotations

from datetime import date
from email.utils import parsedate_to_datetime
from html import unescape
import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from translation_radar_api.models import NormalizedTechnologyRecord, SourceRecord
from translation_radar_api.sources.registry import technology_publisher_host_map
from translation_radar_api.sources.base import SourceAdapter


class InteumRssAdapter(SourceAdapter):
    source_type = "inteum_rss"

    def normalize(self, record: SourceRecord) -> NormalizedTechnologyRecord:
        return NormalizedTechnologyRecord(
            institution_name=record.institution_name,
            source_type=self.source_type,
            source_url=record.source_url,
            title=record.title,
            summary=record.summary,
            contact_name=record.contact_name,
            contact_email=record.contact_email,
            category_tags=record.category_tags,
            posted_on=record.posted_on,
            raw_metadata=record.raw_metadata,
        )


def _parse_feed_date(value: str | None) -> date | None:
    if not value:
        return None

    try:
        return parsedate_to_datetime(value).date()
    except (TypeError, ValueError, IndexError):
        return None


def _find_text(element: ET.Element, local_name: str) -> str | None:
    for child in element.iter():
        if child is element:
            continue
        if child.tag.rsplit("}", 1)[-1] == local_name:
            value = _collect_text(child)
            if value:
                return value
    return None


def _find_all_text(element: ET.Element, local_name: str) -> list[str]:
    values: list[str] = []
    for child in element.iter():
        if child is element:
            continue
        if child.tag.rsplit("}", 1)[-1] == local_name:
            value = _collect_text(child)
            if value:
                values.append(value)
    return values


def _collect_text(element: ET.Element) -> str:
    parts = [part.strip() for part in element.itertext() if part and part.strip()]
    return " ".join(parts).strip()


def _strip_html(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    normalized = re.sub(r"\s+", " ", unescape(without_tags))
    return normalized.strip()


def _split_values(raw_value: str | None, separator: str) -> list[str]:
    if not raw_value:
        return []
    values = [part.strip() for part in raw_value.split(separator)]
    return [value for value in values if value]


def _find_container(element: ET.Element, local_name: str) -> ET.Element | None:
    for child in element.iter():
        if child is element:
            continue
        if child.tag.rsplit("}", 1)[-1] == local_name:
            return child
    return None


def _parse_people(item: ET.Element, list_name: str, item_name: str) -> list[dict[str, str]]:
    container = _find_container(item, list_name)
    if container is None:
        return []

    people: list[dict[str, str]] = []
    for child in container:
        if child.tag.rsplit("}", 1)[-1] != item_name:
            continue
        person: dict[str, str] = {}
        for field in child:
            key = field.tag.rsplit("}", 1)[-1]
            value = _collect_text(field)
            if value:
                person[key] = value
        if person:
            people.append(person)
    return people


def _first_person_name(people: list[dict[str, str]]) -> str | None:
    if not people:
        return None
    first_person = people[0]
    full_name = " ".join(
        part for part in [first_person.get("firstName"), first_person.get("lastName")] if part
    ).strip()
    return full_name or None


def _first_person_email(people: list[dict[str, str]]) -> str | None:
    if not people:
        return None
    return people[0].get("emailAddress")


def _extract_candidate_hosts(text: str) -> list[str]:
    hosts: list[str] = []
    for match in re.findall(r"https?://([^/\s\"'<>]+)", text, flags=re.IGNORECASE):
        host = match.strip().lower()
        if host:
            hosts.append(host)
    return hosts


def _infer_origin_host(item: ET.Element) -> str | None:
    candidates: list[str] = []
    for local_name in ("link", "guid", "description", "image"):
        for value in _find_all_text(item, local_name):
            candidates.extend(_extract_candidate_hosts(value))

    for person in _parse_people(item, "licensingContactList", "licensingContact"):
        email = person.get("emailAddress")
        if email and "@" in email:
            candidates.append(email.split("@", 1)[1].strip().lower())

    for person in _parse_people(item, "inventorList", "inventor"):
        email = person.get("emailAddress")
        if email and "@" in email:
            candidates.append(email.split("@", 1)[1].strip().lower())

    for candidate in candidates:
        parsed_host = urlparse(f"https://{candidate}").hostname or candidate
        parsed_host = parsed_host.lower()
        if parsed_host.endswith(".technologypublisher.com"):
            return parsed_host
    return None


def _infer_institution_name(default_institution_name: str, item: ET.Element) -> str:
    origin_host = _infer_origin_host(item)
    if not origin_host:
        return default_institution_name

    host_map = technology_publisher_host_map()
    return host_map.get(origin_host, default_institution_name)


def parse_inteum_rss_feed(feed_xml: str, institution_name: str, source_url: str) -> list[NormalizedTechnologyRecord]:
    root = ET.fromstring(feed_xml)
    adapter = InteumRssAdapter()
    records: list[NormalizedTechnologyRecord] = []

    for item in root.findall(".//item"):
        title = _find_text(item, "title") or "Untitled technology"
        brief = _find_text(item, "brief")
        description_html = _find_text(item, "description") or ""
        summary = brief or _strip_html(description_html)
        source_id = _find_text(item, "guid") or title
        licensing_contacts = _parse_people(item, "licensingContactList", "licensingContact")
        inventors = _parse_people(item, "inventorList", "inventor")
        contact_name = _first_person_name(licensing_contacts) or _find_text(item, "contactName")
        contact_email = _first_person_email(licensing_contacts) or _find_text(item, "contactEmail")
        categories = [value for value in _find_all_text(item, "category") if value]
        categories.extend(_split_values(_find_text(item, "categoryName"), "|"))
        categories = list(dict.fromkeys(categories))
        keywords = _split_values(_find_text(item, "keywords"), ",")
        posted_on = _parse_feed_date(_find_text(item, "pubDate"))
        inferred_institution_name = _infer_institution_name(institution_name, item)
        origin_host = _infer_origin_host(item)

        raw_metadata = {
            "guid": source_id,
            "link": _find_text(item, "link") or "",
            "author": _find_text(item, "author") or "",
            "caseId": _find_text(item, "caseId") or "",
            "lastUpdateDate": _find_text(item, "lastUpdateDate") or "",
            "origin_host": origin_host or "",
            "description_html": description_html,
            "keywords": keywords,
            "inventors": inventors,
            "licensing_contacts": licensing_contacts,
        }
        for key in (
            "ipStatus",
            "technologyType",
            "developmentStage",
            "trl",
            "problem",
            "solution",
            "technology",
            "advantages",
            "stage",
            "ip",
            "reference",
            "partnerships",
            "docket",
        ):
            value = _find_text(item, key)
            if value:
                raw_metadata[key] = value

        source_record = SourceRecord(
            source_id=source_id,
            institution_name=inferred_institution_name,
            source_type=adapter.source_type,
            source_url=source_url,
            title=title,
            summary=summary,
            contact_name=contact_name,
            contact_email=contact_email,
            category_tags=categories,
            posted_on=posted_on,
            raw_metadata=raw_metadata,
        )
        records.append(adapter.normalize(source_record))

    return records
