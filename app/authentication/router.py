from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
async def register() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/login")
async def login() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/logout")
async def logout() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/introspect")
async def introspect() -> dict[str, str]:
    return {"status": "ok"}
