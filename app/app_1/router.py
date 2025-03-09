from fastapi import APIRouter

router = APIRouter()

@router.get("/healthcheck_app_1_1")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/healthcheck_app_1_1/{parameter_name}")
async def healthcheck(parameter_name: int) -> dict[str, str]:
    return {"status": str(parameter_name)}

@router.get("/healthcheck_app_1_2/{parameter_name}")
async def healthcheck(parameter_name: str) -> dict[str, str]:
    return {"status": parameter_name}