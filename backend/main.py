from __future__ import annotations

from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
MAX_CHARS_PER_FILE = 12000

app = FastAPI(title="File Sentiment API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = pipeline("sentiment-analysis", model=MODEL_NAME, truncation=True)


class FileSentiment(BaseModel):
    filename: str
    label: str
    score: float
    chars_analyzed: int


class SentimentResponse(BaseModel):
    model: str
    total_files: int
    results: List[FileSentiment]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/analyze", response_model=SentimentResponse)
async def analyze(files: List[UploadFile] = File(...)) -> SentimentResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    results: List[FileSentiment] = []

    for uploaded in files:
        raw = await uploaded.read()
        if not raw:
            continue

        try:
            text = raw.decode("utf-8", errors="ignore").strip()
        except Exception as exc:  # defensive
            raise HTTPException(status_code=400, detail=f"Could not read {uploaded.filename}: {exc}")

        if not text:
            continue

        text = text[:MAX_CHARS_PER_FILE]
        prediction = classifier(text)[0]

        results.append(
            FileSentiment(
                filename=uploaded.filename,
                label=prediction["label"],
                score=round(float(prediction["score"]), 4),
                chars_analyzed=len(text),
            )
        )

    if not results:
        raise HTTPException(status_code=400, detail="No readable text found in uploaded files")

    return SentimentResponse(model=MODEL_NAME, total_files=len(results), results=results)
