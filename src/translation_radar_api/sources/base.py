from __future__ import annotations

from abc import ABC, abstractmethod

from translation_radar_api.models import NormalizedTechnologyRecord, SourceRecord


class SourceAdapter(ABC):
    source_type: str

    @abstractmethod
    def normalize(self, record: SourceRecord) -> NormalizedTechnologyRecord:
        """Normalize a source-specific record into the common scouting schema."""
