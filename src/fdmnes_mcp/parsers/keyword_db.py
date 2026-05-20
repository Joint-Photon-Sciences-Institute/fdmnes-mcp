"""
Keyword database for FDMNES, mined from the vault keyword-reference.md doc.

The vault doc is structured as markdown tables with columns:
    Keyword | Aliases | Args | Default | Effect | Source ref

We parse those tables at module import time into a lookup dict.

If the vault doc isn't accessible (different machine, missing path), we ship
a minimal fallback list of the most-used keywords so the MCP still functions
in some degraded mode.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..config import FDMNES_DOCS_DIR


_CATEGORY_HEADER_RE = re.compile(r"^##\s+([A-Z])\.\s+(.+?)\s*$")
_TABLE_ROW_RE = re.compile(r"^\|\s*`([^`|]+)`\s*\|(.*)$")


def _strip_md_inline(s: str) -> str:
    """Remove `backticks` and the surrounding pipes from a markdown cell."""
    s = s.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return s.strip()


def _split_cells(line: str) -> list[str]:
    """Split a markdown table row on |, but not on escaped \\|."""
    # Simple split; FDMNES table cells don't use escaped pipes.
    parts = [c.strip() for c in line.split("|")]
    # First and last are empty due to leading / trailing |
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return parts


def _parse_aliases(cell: str) -> list[str]:
    """Aliases cell is comma-separated, with each alias often in backticks."""
    cell = cell.strip().strip("—-").strip()
    if not cell or cell in {"—", "-"}:
        return []
    # Strip backticks and split on commas.
    return [
        a.strip().strip("`").strip()
        for a in cell.split(",")
        if a.strip().strip("`").strip()
    ]


def _read_keyword_reference() -> dict[str, dict[str, Any]]:
    """Read the keyword-reference.md doc and return a name → record dict."""
    doc = Path(FDMNES_DOCS_DIR) / "keyword-reference.md"
    if not doc.exists():
        return {}

    text = doc.read_text(errors="replace")
    out: dict[str, dict[str, Any]] = {}
    current_category = None

    for line in text.splitlines():
        m = _CATEGORY_HEADER_RE.match(line)
        if m:
            current_category = m.group(2).strip()
            continue
        m = _TABLE_ROW_RE.match(line)
        if not m:
            continue
        name = m.group(1).strip()
        # Re-split the whole row to get all cells.
        cells = _split_cells(line)
        if len(cells) < 5:
            continue
        # Tables vary by section:
        #   6 cells: name | aliases | args | default | effect | source_ref
        #   5 cells: name | aliases | args | effect  | source_ref      (no Default)
        #   4 cells: name | aliases | args | effect                    (no Default, no source_ref)
        aliases = _parse_aliases(cells[1]) if len(cells) > 1 else []
        args = cells[2].strip() if len(cells) > 2 else ""
        default = ""
        effect = ""
        source_ref = ""
        if len(cells) >= 6:
            default = cells[3].strip()
            effect = cells[4].strip()
            source_ref = cells[5].strip()
        elif len(cells) == 5:
            effect = cells[3].strip()
            source_ref = cells[4].strip()
        elif len(cells) == 4:
            effect = cells[3].strip()

        key = name.lower()
        record = {
            "name": name,
            "canonical_9": name[:9].lower(),
            "aliases": aliases,
            "args": args,
            "default": default,
            "effect": effect,
            "source_ref": source_ref,
            "category": current_category,
        }
        out[key] = record
        # Also index by aliases
        for a in aliases:
            out.setdefault(a.lower(), record)
        # And by 9-char canonical
        out.setdefault(name[:9].lower(), record)
    return out


# Module-level cache
_DB: dict[str, dict[str, Any]] | None = None


def get_db() -> dict[str, dict[str, Any]]:
    global _DB
    if _DB is None:
        _DB = _read_keyword_reference() or _FALLBACK_DB
    return _DB


def lookup(name: str) -> dict[str, Any] | None:
    """Look up a keyword (case-insensitive, exact / alias / 9-char prefix)."""
    if not name:
        return None
    db = get_db()
    key = name.strip().lower()
    if key in db:
        return db[key]
    # 9-char canonical
    if key[:9] in db:
        return db[key[:9]]
    # Fallback: any record whose canonical 9-char prefix matches
    for rec in db.values():
        if rec["canonical_9"] == key[:9]:
            return rec
    return None


def search(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Substring search across name / aliases / effect, name-matches first."""
    db = get_db()
    q = query.strip().lower()
    if not q:
        return []
    seen: set[int] = set()
    name_hits: list[dict[str, Any]] = []
    alias_hits: list[dict[str, Any]] = []
    effect_hits: list[dict[str, Any]] = []
    for rec in db.values():
        if id(rec) in seen:
            continue
        if q in rec["name"].lower():
            name_hits.append(rec); seen.add(id(rec))
        elif any(q in a.lower() for a in rec["aliases"]):
            alias_hits.append(rec); seen.add(id(rec))
        elif q in rec["effect"].lower():
            effect_hits.append(rec); seen.add(id(rec))
    return (name_hits + alias_hits + effect_hits)[:limit]


def list_categories() -> list[str]:
    db = get_db()
    cats = []
    seen = set()
    for rec in db.values():
        c = rec.get("category")
        if c and c not in seen:
            cats.append(c)
            seen.add(c)
    return cats


def list_in_category(category: str) -> list[dict[str, Any]]:
    db = get_db()
    seen = set()
    return [
        rec for rec in db.values()
        if rec.get("category") == category and id(rec) not in seen and not seen.add(id(rec))
    ]


# Minimal fallback database (used only if the vault doc can't be loaded).
# Covers the keywords used in the most common pipelines.
_FALLBACK_DB: dict[str, dict[str, Any]] = {
    name.lower(): {
        "name": name,
        "canonical_9": name[:9].lower(),
        "aliases": [],
        "args": args,
        "default": default,
        "effect": effect,
        "source_ref": "",
        "category": cat,
    }
    for (name, args, default, effect, cat) in [
        ("Crystal", "6 reals + atom rows (Z x y z, fractional)", "—", "Periodic unit cell", "Geometry"),
        ("Molecule", "6 reals + atom rows (Z x y z, Cartesian Å)", "—", "Cluster (non-periodic)", "Geometry"),
        ("Cif_file", "1 filename", "—", "Read crystal from CIF", "Geometry"),
        ("Pdb_file", "1 filename", "—", "Read structure from PDB", "Geometry"),
        ("Radius", "1 real (Å) or odd N reals", "3.0", "Cluster radius", "Method"),
        ("Range", "odd N reals: Emin dE1 E1 dE2 ... Emax", "(-5, 0.5, 60)", "Energy grid", "Energy"),
        ("Filout", "1 string", "fdmnes_out", "Output filename prefix", "Top-level"),
        ("Convolution", "0", "off", "Apply arctangent Lorentzian", "Convolution"),
        ("Green", "0", "off (FDM)", "Switch to multiple-scattering", "Method"),
        ("SCF", "0-3 numbers", "off", "Self-consistent field", "SCF"),
        ("TDDFT", "0", "off", "TDDFT post-processing", "Mode"),
        ("Hubbard", "up to ntype reals (U-J in eV)", "0", "DFT+U", "Hubbard"),
        ("Magnetism", "0", "off", "Collinear spin-polarised", "Magnetism"),
        ("Spinorbit", "0", "off", "Spin-orbit in final state", "Magnetism"),
        ("Quadrupole", "0", "off", "Enable E2 multipole channel", "Multipoles"),
        ("Edge", "1 string (K, L23, M45, ...)", "K1", "Edge to compute", "Multipoles"),
        ("Z_absorber", "1+ ints", "—", "Atomic number(s) of absorbers", "Geometry"),
        ("DAFS", "rows of h k l + polarisation codes + azimuth", "—", "Resonant diffraction", "Mode"),
        ("FDMX", "0", "off", "EXAFS-range extension", "Mode"),
        ("End", "0", "—", "Terminate input parsing", "Top-level"),
    ]
}
