import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

load_dotenv(_ROOT / ".env")

from Behaviour.behaviour import BehaviourAnalyzer
from Core.orchestrator import MemoryOrchestrator

app = FastAPI(
    title="AI Life Assistant API",
    description="Hybrid memory router: event, profile, chat, ignore",
)

_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_orchestrator: Optional[MemoryOrchestrator] = None


def get_orchestrator() -> MemoryOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MemoryOrchestrator()
    return _orchestrator


class MessageRequest(BaseModel):
    user_id: str = Field(default="default_user", max_length=100)
    message: str = Field(..., min_length=1)


class QueryRequest(BaseModel):
    user_id: str = Field(default="default_user", max_length=100)
    question: str = Field(..., min_length=1)


def _gemini_error_response(exc: Exception) -> HTTPException:
    err = str(exc)
    if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
        return HTTPException(
            status_code=429,
            detail=(
                "Gemini API quota exceeded (free tier limit). "
                "Wait about 1 minute and try again, or check usage at https://ai.dev/rate-limit. "
                "Your API key is still valid — you do not need a new key unless it was revoked."
            ),
        )
    return HTTPException(status_code=500, detail=f"Processing failed: {exc}")


@app.get("/")
def health():
    return {"status": "ok", "service": "AI Life Assistant"}


@app.post("/message")
def post_message(body: MessageRequest):
    try:
        orch = get_orchestrator()
        result = orch.process_message(body.user_id, body.message.strip())
        return orch.to_dict(result)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise _gemini_error_response(e) from e


@app.post("/query")
def post_query(body: QueryRequest):
    try:
        orch = get_orchestrator()
        answer = orch.query_memory(body.user_id, body.question.strip())
        return {"answer": answer}
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise _gemini_error_response(e) from e


@app.get("/insights")
def get_insights(
    user_id: str = Query(default="default_user"),
    days: int = Query(default=30, ge=1, le=365),
):
    try:
        orch = get_orchestrator()
        analyzer = BehaviourAnalyzer(orch.event_manager, orch.profile_manager)
        return analyzer.analyze(user_id, days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/memory/profile")
def get_profile_memory(user_id: str = Query(default="default_user")):
    try:
        orch = get_orchestrator()
        facts = orch.profile_manager.get_facts(user_id)
        summary = orch.profile_manager.get_profile_summary(user_id)
        return {
            "facts": [f.model_dump(mode="json") for f in facts],
            "summary": summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/memory/events")
def get_event_memory(
    user_id: str = Query(default="default_user"),
    limit: int = Query(default=10, ge=1, le=100),
):
    try:
        orch = get_orchestrator()
        events = orch.event_manager.get_recent_events(user_id, limit=limit)
        analytics = orch.event_manager.get_behavioral_analytics(user_id, days=30)
        return {
            "events": [e.model_dump(mode="json") for e in events],
            "analytics": analytics,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True,
    )
