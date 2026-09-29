from collections import defaultdict, deque
from time import monotonic

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from .config import Settings
from .service import AnalyticsService


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class Limiter:
    def __init__(self, per_minute: int):
        self.per_minute, self.history = per_minute, defaultdict(deque)

    def allow(self, key: str) -> bool:
        now, bucket = monotonic(), self.history[key]
        while bucket and bucket[0] <= now - 60:
            bucket.popleft()
        if len(bucket) >= self.per_minute:
            return False
        bucket.append(now)
        return True


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    service, limiter = AnalyticsService(settings), Limiter(settings.requests_per_minute)
    app = FastAPI(title="Enterprise Text-to-SQL Agent", version="0.1.0")
    app.state.service = service

    def authenticate(x_api_key: str = Header(default="")):
        if len(settings.api_key) < 24 or x_api_key != settings.api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")

    @app.get("/health")
    def health():
        return service.health()

    @app.post("/v1/analytics", dependencies=[Depends(authenticate)])
    def analytics(body: Question, request: Request):
        client = request.client.host if request.client else "unknown"
        if not limiter.allow(client):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        return service.ask(body.question)

    return app
