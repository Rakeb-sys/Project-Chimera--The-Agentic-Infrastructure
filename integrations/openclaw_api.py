from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict
import uvicorn

app = FastAPI(title="OpenClaw Mock API")

class AnalyzeRequest(BaseModel):
    text: str
    meta: Dict[str, Any] = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    text = req.text or ""
    tokens = len(text.split())
    return {
        "input": {"text": text, "meta": req.meta},
        "summary": text[:200],
        "tokens": tokens,
        "insights": {
            "length": len(text),
            "word_count": tokens,
            "mock_label": "mock_insight"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)