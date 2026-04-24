"""CLI adapter."""

from __future__ import annotations

try:
    import typer
except ImportError:  # pragma: no cover - exercised only without optional deps
    typer = None


app = typer.Typer(help="net2vec command line tools") if typer else None
