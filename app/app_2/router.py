from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/healthcheck2")
async def healthcheck() -> dict[str, str]:
    return {"status": "ko"}

@router.post("/healthcheck2")
async def healthcheck() -> dict[str, str]:
    return {"status": "ko"}

@router.delete("/healthcheck2")
async def healthcheck() -> dict[str, str]:
    return {"status": "ko"}