"""FastAPI application factory."""

from __future__ import annotations

try:
    from fastapi import FastAPI
except ImportError:  # pragma: no cover - exercised only without optional deps
    FastAPI = None  # type: ignore[assignment]


def create_app():
    """Create the API application with a health route."""
    if FastAPI is None:
        raise RuntimeError("FastAPI is required to run the API")

    app = FastAPI(title="net2vec")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app() if FastAPI is not None else None
