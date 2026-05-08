"""FastAPI application factory."""

from __future__ import annotations

try:
    from fastapi import FastAPI
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
except ImportError:  # pragma: no cover - exercised only without optional deps
    FastAPI = None  # type: ignore[assignment]
    RequestValidationError = None  # type: ignore[assignment]
    JSONResponse = None  # type: ignore[assignment]


def create_app(search_service=None, ingestion_pipeline=None):  # noqa: ANN001
    """Create the API application with a health route."""
    if FastAPI is None:
        raise RuntimeError("FastAPI is required to run the API")

    from net2vec.api.routes import create_router

    app = FastAPI(title="net2vec")
    app.add_exception_handler(RequestValidationError, _validation_error_response)
    app.include_router(create_router(search_service, ingestion_pipeline))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def _validation_error_response(request, exc):  # noqa: ANN001, ARG001
    return JSONResponse(
        status_code=400,
        content={"error": "invalid_request", "detail": str(exc)},
    )


app = create_app() if FastAPI is not None else None
