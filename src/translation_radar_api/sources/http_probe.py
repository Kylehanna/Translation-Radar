from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
import ssl
import urllib.request


class _TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title and data.strip():
            self._parts.append(data.strip())

    @property
    def title(self) -> str:
        return " ".join(self._parts).strip()


@dataclass
class UrlProbeResult:
    success: bool
    http_status: int | None = None
    final_url: str = ""
    title: str = ""
    error: str = ""


def probe_url(url: str, timeout_seconds: int = 10) -> UrlProbeResult:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds, context=ssl_context) as response:
            body = response.read(50000).decode("utf-8", errors="ignore")
            parser = _TitleParser()
            parser.feed(body)
            return UrlProbeResult(
                success=True,
                http_status=getattr(response, "status", response.getcode()),
                final_url=response.geturl(),
                title=parser.title,
            )
    except Exception as exc:  # pragma: no cover - network failure surface
        return UrlProbeResult(success=False, error=str(exc))