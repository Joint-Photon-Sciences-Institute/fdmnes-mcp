"""
Parser for FDMNES spectrum output files.

FDMNES writes two main spectrum formats:

  X.txt           Unconvolved spectrum. First line is a metadata line
                  ("E_edge, Z, n_edge, j_edge, ..."); second line is
                  column names; data follows. With DAFS or polarisations,
                  additional columns are appended.

  X_conv.txt      Convolved spectrum. Simpler format: just energy +
                  cross-section columns (sometimes with intensities or
                  Stokes parameters for RXS).

Both are whitespace-separated text. We try metadata extraction first, then
fall back to a "columns + numeric block" read.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np


_NUM_RE = re.compile(r"^[\s\-+0-9.eEdD]+$")


def _is_numeric_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    # Lines that are entirely numeric tokens.
    try:
        tokens = stripped.split()
        for t in tokens:
            float(t.replace("D", "e").replace("d", "e"))
        return True
    except ValueError:
        return False


def parse_spectrum(path: str | Path) -> dict[str, Any]:
    """
    Parse a FDMNES spectrum file (X.txt or X_conv.txt).

    Returns a dict with:
      - file: original path
      - kind: 'unconvolved' | 'convolved' | 'unknown'
      - header_meta: dict of any leading metadata (E_edge, Z, ...)
      - columns: list of column names
      - data: dict[colname -> 1D numpy array]
      - n_points: int
    """
    path = Path(path)
    text = path.read_text(errors="replace")
    lines = text.splitlines()

    # Find first numeric line; everything before is header/metadata.
    data_start = None
    for i, ln in enumerate(lines):
        if _is_numeric_line(ln) and len(ln.split()) >= 2:
            data_start = i
            break
    if data_start is None:
        return {
            "file": str(path),
            "kind": "unknown",
            "error": "no numeric data block found",
            "header_meta": {},
            "columns": [],
            "data": {},
            "n_points": 0,
        }

    header_lines = lines[:data_start]
    column_line = header_lines[-1] if header_lines else ""

    # Try column-names: any non-numeric header line that has multiple tokens.
    cols = column_line.split()
    # X.txt's column-name line is preceded by a metadata line ending in '...'
    # Heuristic: if the line above also has tokens that look like words, the
    # last header line is the column header.
    if not cols or _is_numeric_line(column_line):
        cols = []

    # Extract numeric block.
    data_block: list[list[float]] = []
    for ln in lines[data_start:]:
        if not ln.strip():
            continue
        if not _is_numeric_line(ln):
            break  # trailing comment / footer
        toks = ln.replace("D", "e").replace("d", "e").split()
        try:
            data_block.append([float(t) for t in toks])
        except ValueError:
            break

    if not data_block:
        return {
            "file": str(path),
            "kind": "unknown",
            "error": "empty numeric block",
            "header_meta": {},
            "columns": cols,
            "data": {},
            "n_points": 0,
        }

    # Rectangular numpy array
    max_cols = max(len(r) for r in data_block)
    arr = np.full((len(data_block), max_cols), np.nan)
    for i, r in enumerate(data_block):
        arr[i, : len(r)] = r

    # Pad column names if short
    if len(cols) < max_cols:
        cols = cols + [f"col{i+1}" for i in range(len(cols), max_cols)]

    # Header-meta extraction: find an "E_edge, Z, ..." line.
    header_meta: dict[str, Any] = {}
    for hl in header_lines:
        if "=" in hl and "E_edge" in hl:
            # Format example:
            #   8979.000   29  1  1  1.5...  = E_edge, Z, n_edge, j_edge, ...
            left, right = hl.split("=", 1)
            keys = [k.strip() for k in right.strip().split(",")]
            vals = left.strip().split()
            for k, v in zip(keys, vals):
                try:
                    header_meta[k] = float(v) if "." in v or "e" in v.lower() else int(v)
                except ValueError:
                    header_meta[k] = v

    # Decide kind
    kind = "unknown"
    p = str(path)
    if "_conv" in p:
        kind = "convolved"
    elif p.endswith(".txt") and header_meta:
        kind = "unconvolved"
    elif p.endswith(".txt"):
        kind = "convolved"

    data = {cols[i]: arr[:, i] for i in range(max_cols)}

    return {
        "file": str(path),
        "kind": kind,
        "header_meta": header_meta,
        "columns": cols,
        "data": data,
        "n_points": int(arr.shape[0]),
    }


def summarise_spectrum(parsed: dict) -> dict:
    """Compact summary suitable as a tool return value (arrays elided)."""
    out = {
        "file": parsed.get("file"),
        "kind": parsed.get("kind"),
        "n_points": parsed.get("n_points"),
        "columns": parsed.get("columns"),
        "header_meta": parsed.get("header_meta", {}),
    }
    data = parsed.get("data") or {}
    if data and "Energy" in data or "energy" in data:
        ekey = "Energy" if "Energy" in data else "energy"
        e = data[ekey]
        out["energy_range"] = [float(e[0]), float(e[-1])]
        out["energy_step_mean"] = float(np.diff(e).mean()) if len(e) > 1 else None
    # Min/max of the second column (typical XANES col)
    if parsed.get("columns") and len(parsed["columns"]) >= 2:
        c2 = parsed["columns"][1]
        v = data.get(c2)
        if v is not None and len(v):
            out["second_column"] = c2
            out["second_column_min"] = float(np.nanmin(v))
            out["second_column_max"] = float(np.nanmax(v))
    return out
