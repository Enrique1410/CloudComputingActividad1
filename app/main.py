from fastapi import FastAPI

from app.authentication.router import router as router_auth
from app.files.router import router as router_files

app = FastAPI()

app.include_router(router_auth)
app.include_router(router_files, prefix="/files")
