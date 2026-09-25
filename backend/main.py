from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.models import TaskRequest
from backend.orchestration.workflow import execute
from backend.llm.client import llm
from pathlib import Path

app = FastAPI(title="VeritasMesh — Verification-First Multi-Agent Engine")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
ROOT = Path(__file__).resolve().parent.parent

@app.get("/")
def home():
    return FileResponse(ROOT / "frontend" / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "llm_enabled": llm.enabled, "model": llm.model if llm.enabled else None}

@app.post("/api/tasks")
def task(req: TaskRequest):
    return execute(req.task)
