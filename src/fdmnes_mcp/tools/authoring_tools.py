"""Authoring & validation tools (build / validate / lookup inputs)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import config
from ..parsers import input_parser, keyword_db


def fdmnes_keyword_lookup(name: str) -> dict[str, Any]:
    """Look up an FDMNES keyword by canonical name or alias.

    Args:
      name: the keyword (case-insensitive; aliases also accepted).

    Returns: {name, aliases, args, default, effect, source_ref, category}
    or {error: "not found"}.
    """
    rec = keyword_db.lookup(name)
    if rec is None:
        return {"error": f"keyword '{name}' not found in the FDMNES keyword DB"}
    return {k: v for k, v in rec.items() if k != "canonical_9"}


def fdmnes_keyword_search(query: str, limit: int = 20) -> dict[str, Any]:
    """Search the FDMNES keyword DB by substring (name / alias / effect text).

    Args:
      query: substring to match against keyword name, aliases, or effect.
      limit: max hits to return.

    Returns: list of records, name-matches first.
    """
    hits = keyword_db.search(query, limit=limit)
    return {
        "query": query,
        "n_hits": len(hits),
        "hits": [{k: v for k, v in h.items() if k != "canonical_9"} for h in hits],
    }


def fdmnes_list_keyword_categories() -> dict[str, Any]:
    """List the keyword categories in the FDMNES keyword DB."""
    cats = keyword_db.list_categories()
    return {"n": len(cats), "categories": cats}


def fdmnes_validate_input(path_or_content: str) -> dict[str, Any]:
    """Lint an FDMNES `_inp.txt` against the keyword DB.

    Args:
      path_or_content: either a path to an `_inp.txt` file, or the file
        content as a string.

    Returns: a list of issues, each with type (error|warning|note),
    keyword, lineno, and message.
    """
    parsed = input_parser.parse_input(path_or_content)
    issues = []

    if not parsed["has_end"]:
        issues.append({
            "type": "error",
            "keyword": None,
            "lineno": None,
            "message": "Missing 'End' keyword — FDMNES will refuse to stop parsing.",
        })

    has_structure = False
    structure_kws = {"crystal", "molecule", "film", "surface", "cif_file", "pdb_file", "flapw"}
    for b in parsed["blocks"]:
        kw = b["keyword"]
        kw_l = kw.lower()
        if kw_l in structure_kws or kw_l[:9] in structure_kws:
            has_structure = True
        rec = keyword_db.lookup(kw)
        if rec is None:
            issues.append({
                "type": "warning",
                "keyword": kw,
                "lineno": b["lineno"],
                "message": f"Unknown keyword '{kw}' (not in keyword DB; could be a typo or a recent addition).",
            })

    if not has_structure:
        issues.append({
            "type": "error",
            "keyword": None,
            "lineno": None,
            "message": "No structure block found (need one of Crystal / Molecule / Film / Surface / Cif_file / Pdb_file / Flapw).",
        })

    # Check for Radius
    if "radius" not in parsed["keywords"]:
        issues.append({
            "type": "warning",
            "keyword": None,
            "lineno": None,
            "message": "No 'Radius' keyword. FDMNES will use default 3.0 Å — usually too small for production.",
        })

    return {
        "n_blocks": parsed["n_blocks"],
        "has_end": parsed["has_end"],
        "n_issues": len(issues),
        "issues": issues,
    }


def fdmnes_build_input(
    *,
    output_path: str | None = None,
    filout: str,
    structure_kind: str,
    structure_args: list[str],
    atoms: list[list],
    radius: float = 5.0,
    energy_range: list[float] | None = None,
    edge: str | None = None,
    z_absorber: int | None = None,
    extra_keywords: dict[str, str | list[str] | None] | None = None,
    convolution: bool = True,
) -> dict[str, Any]:
    """Build a FDMNES `_inp.txt` from structured parameters.

    Args:
      output_path: if set, write the generated input to this path. Otherwise
        only return the text.
      filout: value for the `Filout` block (output prefix, without extension).
      structure_kind: 'crystal' | 'molecule' | 'film' | 'surface' | 'cif_file'
        | 'pdb_file'.
      structure_args: list of strings making up the structure header line.
        For 'crystal': ['a', 'b', 'c', 'alpha', 'beta', 'gamma'] (as strings).
        For 'cif_file' / 'pdb_file': single-element list with the filename.
      atoms: list of atom rows for the structure block. Each row is a list
        like [Z, x, y, z] (numbers or strings). Ignored for cif_file / pdb_file.
      radius: cluster radius in Å.
      energy_range: 3 or more values: [Emin, dE1, E1, dE2, ..., Emax]. If None,
        uses default [-5, 0.5, 60].
      edge: edge string (K, L23, M5, ...). If None, FDMNES picks the default.
      z_absorber: atomic number of the absorber(s). If None, FDMNES uses the
        first atom in the structure.
      extra_keywords: dict of additional keyword → value (string, list of
        strings, or None for parameterless keywords).
      convolution: if True (default), add a `Convolution` block.

    Returns: {text: the generated input, path: written path if any}.
    """
    lines: list[str] = []
    lines.append("! FDMNES input generated by fdmnes-mcp")
    lines.append("")

    lines.append(" Filout")
    lines.append(f"   {filout}")
    lines.append("")

    if energy_range is None:
        energy_range = [-5.0, 0.5, 60.0]
    lines.append(" Range")
    lines.append("   " + " ".join(f"{x}" for x in energy_range))
    lines.append("")

    lines.append(" Radius")
    lines.append(f"   {radius}")
    lines.append("")

    if edge:
        lines.append(" Edge")
        lines.append(f"   {edge}")
        lines.append("")

    if z_absorber is not None:
        lines.append(" Z_absorber")
        lines.append(f"   {z_absorber}")
        lines.append("")

    kind = structure_kind.lower()
    cap = {"crystal": "Crystal", "molecule": "Molecule", "film": "Film",
           "surface": "Surface", "cif_file": "Cif_file", "pdb_file": "Pdb_file"}
    block_name = cap.get(kind)
    if not block_name:
        return {"error": f"unknown structure_kind '{structure_kind}'"}
    lines.append(f" {block_name}")
    if kind in ("cif_file", "pdb_file"):
        if not structure_args:
            return {"error": f"{structure_kind} needs one filename in structure_args"}
        lines.append(f"   {structure_args[0]}")
    else:
        lines.append("   " + " ".join(str(x) for x in structure_args))
        for row in atoms:
            lines.append("   " + " ".join(str(x) for x in row))
    lines.append("")

    if extra_keywords:
        for kw, val in extra_keywords.items():
            lines.append(f" {kw}")
            if val is None or val == "":
                pass
            elif isinstance(val, (list, tuple)):
                for v in val:
                    lines.append(f"   {v}")
            else:
                lines.append(f"   {val}")
            lines.append("")

    if convolution:
        lines.append(" Convolution")
        lines.append("")

    lines.append(" End")
    lines.append("")
    text = "\n".join(lines)

    out: dict[str, Any] = {"text": text, "n_lines": len(lines)}
    if output_path:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        out["path"] = str(p)
    return out
