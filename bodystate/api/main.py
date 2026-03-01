# bodystate/api/main.py

from fastapi import FastAPI
from bodystate.api.schemas import EngineRequest
from bodystate.api.engine_service import EngineService

app = FastAPI(
    title="Body-State Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/compute")
def compute_engine(payload: EngineRequest):
    result = EngineService.run(payload.model_dump())
    return result
    