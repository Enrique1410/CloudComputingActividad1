from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.authentication.api.router import router as router_auth
from app.files.router import router as router_files
from app.config import DATABASE_URL, models

app = FastAPI()

app.include_router(router_auth)
app.include_router(router_files, prefix="/files")

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": models},
    generate_schemas=False,
    add_exception_handlers=True,
)
