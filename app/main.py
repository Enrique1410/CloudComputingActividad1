from fastapi import FastAPI
from app.app_1.router import router as router_app_1
from app.app_2.router import router as router_app_2

app = FastAPI()

app.include_router(router_app_1)
app.include_router(router_app_2, prefix="/app_2")