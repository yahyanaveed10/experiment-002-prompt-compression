"""FastAPI entry point for Experiment 002."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.embeddings import DEFAULT_MODEL, get_embedder
from app.scenarios import SCENARIOS
from app.selector import ContextChunk, select_context

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="Experiment 002",
    description="Embedding-based context selection without a generative LLM.",
    version="0.1.0",
)


class ChunkInput(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
    is_evidence: bool | None = None


class SelectionInput(BaseModel):
    query: str = Field(min_length=1, max_length=2_000)
    chunks: list[ChunkInput] = Field(min_length=1, max_length=100)
    strategy: Literal["budget", "adaptive"] = "budget"
    budget_percent: int = Field(default=40, ge=1, le=100)
    similarity_threshold: float = Field(default=0.4, ge=-1, le=1)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "model": DEFAULT_MODEL}


@app.get("/api/scenarios")
def scenarios() -> list[dict]:
    return SCENARIOS


@app.post("/api/select")
def select(payload: SelectionInput) -> dict:
    try:
        return select_context(
            payload.query,
            [
                ContextChunk(chunk.text, chunk.is_evidence)
                for chunk in payload.chunks
            ],
            get_embedder(),
            strategy=payload.strategy,
            budget_percent=payload.budget_percent,
            similarity_threshold=payload.similarity_threshold,
        )
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
