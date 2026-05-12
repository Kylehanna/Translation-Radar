from fastapi import APIRouter

from translation_radar_api.models import ScoutSignalRequest, ScoutSignalResponse
from translation_radar_api.services.scout_signal import build_scout_signals


router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/scout-signals", response_model=ScoutSignalResponse)
def scout_signal_alerts(payload: ScoutSignalRequest) -> ScoutSignalResponse:
    return build_scout_signals(payload.researchers, minimum_score=payload.minimum_score)