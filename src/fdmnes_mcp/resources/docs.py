"""
Expose the FDMNES vault docs as MCP resources at fdmnes://docs/*.

Resource URIs registered:
  fdmnes://docs/overview          ← 2026-05-19-docs-overview.md (index)
  fdmnes://docs/install           ← 2026-05-19-install.md
  fdmnes://docs/methods           ← methods-and-theory.md
  fdmnes://docs/io                ← inputs-and-outputs.md
  fdmnes://docs/keywords          ← keyword-reference.md
  fdmnes://docs/pipelines         ← pipelines.md
  fdmnes://docs/examples          ← examples-catalog.md
  fdmnes://docs/operations        ← operations-on-llmbox.md
  fdmnes://docs/keyword/{name}    ← per-keyword reference card
  fdmnes://config                 ← server configuration snapshot
"""
from __future__ import annotations

import json
from pathlib import Path

from .. import config
from ..parsers import keyword_db


DOC_SOURCES = {
    "methods": "methods-and-theory.md",
    "io": "inputs-and-outputs.md",
    "keywords": "keyword-reference.md",
    "pipelines": "pipelines.md",
    "examples": "examples-catalog.md",
}


def _read_doc(slug: str) -> str:
    fname = DOC_SOURCES.get(slug)
    if not fname:
        return f"# {slug}\n\nUnknown doc slug. Available: {sorted(DOC_SOURCES)}"
    p = Path(config.FDMNES_DOCS_DIR) / fname
    if not p.exists():
        return f"# {slug}\n\nDoc file not found: {p}"
    return p.read_text(errors="replace")


def register_resources(mcp) -> None:
    """Register all FDMNES docs / config resources with the FastMCP server."""

    @mcp.resource("fdmnes://config")
    def _config() -> str:
        """Current server paths and defaults (FDMNES binary, examples dir, docs dir, MPI count)."""
        return json.dumps(config.summary(), indent=2)

    @mcp.resource("fdmnes://docs/methods")
    def _docs_methods() -> str:
        """FDM vs MST, DFT/TDDFT, defaults, limitations."""
        return _read_doc("methods")

    @mcp.resource("fdmnes://docs/io")
    def _docs_io() -> str:
        """Input file grammar and output file catalog."""
        return _read_doc("io")

    @mcp.resource("fdmnes://docs/keywords")
    def _docs_keywords() -> str:
        """Full ~350-keyword reference (large)."""
        return _read_doc("keywords")

    @mcp.resource("fdmnes://docs/pipelines")
    def _docs_pipelines() -> str:
        """16 workflow recipes (XANES, SCF, RXS, RIXS, XMCD, ...)."""
        return _read_doc("pipelines")

    @mcp.resource("fdmnes://docs/examples")
    def _docs_examples() -> str:
        """Annotated catalog of the bundled FDMNES test inputs."""
        return _read_doc("examples")

    # Per-keyword card — templated resource URI
    @mcp.resource("fdmnes://docs/keyword/{name}")
    def _docs_keyword(name: str) -> str:
        """Reference card for a single FDMNES keyword (by canonical name or alias)."""
        rec = keyword_db.lookup(name)
        if rec is None:
            return f"# {name}\n\nNot found in the FDMNES keyword DB."
        return (
            f"# `{rec['name']}`\n\n"
            f"**Category**: {rec.get('category', '—')}\n\n"
            f"**Aliases**: {', '.join(rec['aliases']) if rec['aliases'] else '—'}\n\n"
            f"**Arguments**: {rec['args'] or '—'}\n\n"
            f"**Default**: {rec['default'] or '—'}\n\n"
            f"**Effect**: {rec['effect'] or '—'}\n\n"
            f"**Source**: {rec['source_ref'] or '—'}\n"
        )
