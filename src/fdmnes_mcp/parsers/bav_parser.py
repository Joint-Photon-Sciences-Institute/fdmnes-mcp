"""
Parser for FDMNES *_bav.txt verbose log files.

bav files can run to many megabytes; we extract structured highlights:
  - release banner + date
  - parsed input echo
  - Symsite (space group / non-equivalent atoms)
  - Agregat (built cluster around each absorber)
  - point group
  - Fermi level
  - SCF convergence trace (if present)
  - convolution Γ(E) curve (if present)
  - total wall time
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


_RELEASE_RE = re.compile(r"FDMNES program,\s*Revision\s*(.+?)\s*$")
_DATE_RE = re.compile(r"Date\s*=\s*(\S+\s*\S*\s*\S*)")
_TIME_RE = re.compile(r"Time\s*=\s*(.+)")
_FERMI_RE = re.compile(r"E_Fermi\s*=\s*(\S+)", re.IGNORECASE)
_TOTAL_TIME_RE = re.compile(r"Total time\s*=\s*(\S+)\s*s", re.IGNORECASE)
_POINTGROUP_RE = re.compile(r"point group\s*[:=]?\s*(\S+)", re.IGNORECASE)


def _section(lines: list[str], start_pat: str, n_lines: int = 30) -> list[str]:
    """Return up to n_lines after the first line matching start_pat."""
    rx = re.compile(start_pat, re.IGNORECASE)
    for i, ln in enumerate(lines):
        if rx.search(ln):
            return lines[i : i + n_lines]
    return []


def parse_bav(path: str | Path, *, full_text: bool = False) -> dict[str, Any]:
    """
    Parse a *_bav.txt file. Returns highlights; the full text is included only
    if `full_text=True`.
    """
    path = Path(path)
    text = path.read_text(errors="replace")
    lines = text.splitlines()
    n_lines = len(lines)
    out: dict[str, Any] = {
        "file": str(path),
        "n_lines": n_lines,
        "size_bytes": path.stat().st_size,
    }

    # Release banner / date / time
    for ln in lines[:40]:
        m = _RELEASE_RE.search(ln)
        if m:
            out["release"] = m.group(1).strip()
        m = _DATE_RE.search(ln)
        if m:
            out["date"] = m.group(1).strip()
        m = _TIME_RE.search(ln)
        if m:
            out["time"] = m.group(1).strip()

    # Threshold / edge
    for ln in lines[:120]:
        if "Threshold" in ln:
            out["threshold"] = ln.strip()
            break

    # Symsite section
    sym = _section(lines, r"^\s*Symsite", n_lines=40)
    if sym:
        out["symsite_excerpt"] = "\n".join(sym).rstrip()

    # Agregat section
    agg = _section(lines, r"^\s*Agregat|^\s*Cluster", n_lines=40)
    if agg:
        out["agregat_excerpt"] = "\n".join(agg).rstrip()

    # Point group
    for ln in lines[:300]:
        m = _POINTGROUP_RE.search(ln)
        if m:
            out["point_group"] = m.group(1).strip()
            break

    # SCF trace: lines containing "Cycle" or "iter" with energy
    scf_lines = [ln for ln in lines if re.search(r"\bcycle\b|\bSCF\b", ln, re.IGNORECASE)]
    if scf_lines:
        out["scf_trace_excerpt"] = "\n".join(scf_lines[:30])
        out["scf_trace_n_matches"] = len(scf_lines)

    # Fermi level
    for ln in lines:
        m = _FERMI_RE.search(ln)
        if m:
            try:
                out["fermi_eV"] = float(m.group(1))
            except ValueError:
                pass
            break

    # Total wall time (often near end)
    for ln in lines[-60:]:
        m = _TOTAL_TIME_RE.search(ln)
        if m:
            try:
                out["total_cpu_seconds"] = float(m.group(1))
            except ValueError:
                pass
            break

    # Parallel banner
    for ln in lines[:200]:
        if "Parallel calculation" in ln or "MUMPS Solver" in ln:
            out["parallel_banner"] = ln.strip()
            break

    if full_text:
        out["full_text"] = text

    return out
