from fastapi import APIRouter

from translation_radar_api.models import DisclosureGapRequest, DisclosureGapResponse
from translation_radar_api.services.disclosure_gap import build_gap_alerts


router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/disclosure-gap", response_model=DisclosureGapResponse)
def disclosure_gap_alerts(payload: DisclosureGapRequest) -> DisclosureGapResponse:
    return build_gap_alerts(payload.researchers, minimum_score=payload.minimum_score)