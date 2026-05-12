from fastapi import APIRouter, HTTPException

from translation_radar_api.models import (
    RagCoverageStatus,
    RagIndexBuildResponse,
    RagIndexStatusResponse,
    RagSearchRequest,
    RagSearchResponse,
    RagTechnologyDetail,
)
from translation_radar_api.services.rag_search import (
    build_rag_coverage_status,
    build_seed_rag_index,
    get_seed_technology_detail,
    get_seed_rag_index_status,
    search_seed_technology_records,
)


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/search", response_model=RagSearchResponse)
def rag_search(payload: RagSearchRequest) -> RagSearchResponse:
    return search_seed_technology_records(payload)


@router.get("/coverage", response_model=RagCoverageStatus)
def rag_coverage() -> RagCoverageStatus:
    return build_rag_coverage_status()


@router.post("/index/build", response_model=RagIndexBuildResponse)
def rag_build_index() -> RagIndexBuildResponse:
    return build_seed_rag_index()


@router.get("/index/status", response_model=RagIndexStatusResponse)
def rag_index_status() -> RagIndexStatusResponse:
    return get_seed_rag_index_status()


@router.get("/technologies/{technology_id}", response_model=RagTechnologyDetail)
def rag_technology_detail(technology_id: str) -> RagTechnologyDetail:
    detail = get_seed_technology_detail(technology_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Technology not found")
    return detail