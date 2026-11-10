from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the API. Settings can be injected so tests can vary key and origin."""
    settings = settings or Settings()
    app = FastAPI(title="PDF Chatbot API")

    # Only the configured frontend origin may call the API from a browser.
    # Later changes that add other HTTP methods must extend allow_methods.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_methods=["GET"],
        allow_headers=["Content-Type"],
        allow_credentials=False,
    )

    @app.get("/api/health")
    def health() -> dict:
        # No I/O and no external calls: reports readiness only, never the key.
        return {"status": "ok", "groq_configured": settings.groq_configured}

    return app


app = create_app()
