"""I/O and inspection tools."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .. import config
from ..parsers import bav_parser, input_parser, spectrum_parser


def fdmnes_get_config() -> dict[str, Any]:
    """Show the MCP server's current paths and defaults.

    Useful for confirming the server can see the FDMNES binary, the examples
    directory, and the vault docs.
    """
    return config.summary()


def fdmnes_list_examples() -> dict[str, Any]:
    """List the bundled FDMNES Test_stand examples (`Sim/Test_stand/in/*_inp.txt`).

    Returns one entry per example with: path, name (short), and a one-line
    description guessed from the first non-blank comment line.
    """
    d = Path(config.FDMNES_EXAMPLES_DIR)
    if not d.exists():
        return {"error": f"examples dir not found: {d}", "examples": []}
    items = []
    for f in sorted(d.glob("*_inp.txt")):
        # Find the first '!' comment line
        desc = ""
        try:
            for line in f.read_text(errors="replace").splitlines()[:8]:
                s = line.strip()
                if s.startswith("!") and len(s) > 2:
                    desc = s.lstrip("!").strip()
                    break
        except Exception:
            pass
        items.append({
            "name": f.stem.replace("_inp", ""),
            "path": str(f),
            "description": desc,
        })
    return {"count": len(items), "examples_dir": str(d), "examples": items}


def fdmnes_read_input(path: str) -> dict[str, Any]:
    """Parse an FDMNES `_inp.txt` file into structured blocks.

    Args:
      path: absolute or cwd-relative path to the `_inp.txt`.

    Returns:
      n_blocks, has_end, blocks (list of {keyword, values, lineno}),
      keywords (dict[keyword → [blocks]]), source path.
    """
    p = Path(path)
    if not p.exists():
        return {"error": f"file not found: {p}"}
    parsed = input_parser.parse_input(p)
    # Truncate value arrays in summary for compactness
    summary_blocks = []
    for b in parsed["blocks"]:
        summary_blocks.append({
            "keyword": b["keyword"],
            "lineno": b["lineno"],
            "n_value_lines": len(b["values"]),
            "values_preview": b["values"][:5],
        })
    return {
        "path": parsed.get("path"),
        "n_blocks": parsed["n_blocks"],
        "has_end": parsed["has_end"],
        "keywords_present": sorted(parsed["keywords"].keys()),
        "blocks_summary": summary_blocks,
    }


def fdmnes_read_spectrum(path: str, max_points: int = 1000) -> dict[str, Any]:
    """Parse an FDMNES spectrum file (`X.txt` or `X_conv.txt`) into arrays.

    Args:
      path: absolute or cwd-relative path.
      max_points: if the spectrum has more rows than this, downsample
        uniformly so the returned arrays stay small in the MCP transport.

    Returns:
      file, kind (unconvolved/convolved), header_meta (E_edge, Z, ...),
      columns, data (dict[colname → list of floats]), n_points.
    """
    p = Path(path)
    if not p.exists():
        return {"error": f"file not found: {p}"}
    parsed = spectrum_parser.parse_spectrum(p)
    if "error" in parsed:
        return parsed

    n = parsed["n_points"]
    data = parsed["data"]
    if n > max_points:
        idx = np.linspace(0, n - 1, max_points).astype(int)
        data = {k: v[idx].tolist() for k, v in data.items()}
        downsampled = True
    else:
        data = {k: v.tolist() for k, v in data.items()}
        downsampled = False

    return {
        "file": parsed["file"],
        "kind": parsed["kind"],
        "header_meta": parsed.get("header_meta", {}),
        "columns": parsed["columns"],
        "n_points": n,
        "downsampled_to": (len(next(iter(data.values()))) if data else 0) if downsampled else None,
        "data": data,
    }


def fdmnes_summarise_spectrum(path: str) -> dict[str, Any]:
    """Compact summary (no arrays) of an FDMNES spectrum file.

    Same as `fdmnes_read_spectrum` but returns only metadata + ranges,
    not the data arrays. Cheaper for "what's in this file" questions.
    """
    p = Path(path)
    if not p.exists():
        return {"error": f"file not found: {p}"}
    parsed = spectrum_parser.parse_spectrum(p)
    return spectrum_parser.summarise_spectrum(parsed)


def fdmnes_read_bav(path: str, full_text: bool = False) -> dict[str, Any]:
    """Extract structured highlights from a `*_bav.txt` diagnostic log.

    Args:
      path: absolute path to the bav file.
      full_text: if True include the entire file content (can be MB-sized).

    Returns: release, date, time, threshold, point_group, symsite_excerpt,
    agregat_excerpt, scf_trace_excerpt, fermi_eV, total_cpu_seconds,
    parallel_banner.
    """
    p = Path(path)
    if not p.exists():
        return {"error": f"file not found: {p}"}
    return bav_parser.parse_bav(p, full_text=full_text)


def fdmnes_list_outputs(prefix_or_dir: str) -> dict[str, Any]:
    """List FDMNES output files matching a prefix or sitting in a directory.

    Args:
      prefix_or_dir: either an output prefix (`Sim/Test_stand/Cu`) — in which
        case we glob `<prefix>*` — or a directory path, in which case we list
        all `.txt` files under it.

    Returns: list of {path, size_bytes, kind_guess}.
    """
    p = Path(prefix_or_dir)
    if p.is_dir():
        candidates = sorted(p.glob("*.txt"))
    else:
        candidates = sorted(p.parent.glob(p.name + "*"))
    out = []
    for f in candidates:
        if not f.is_file():
            continue
        kind = "spectrum"
        name = f.name
        if name.endswith("_bav.txt"):
            kind = "bav (diagnostic log)"
        elif name.endswith("_conv.txt"):
            kind = "convolved spectrum"
        elif name.endswith("_scan.txt"):
            kind = "azimuthal scan"
        elif name.endswith("_scan_conv.txt"):
            kind = "convolved azimuthal scan"
        elif "_sd" in name:
            kind = "projected DOS"
        elif "_tddft" in name:
            kind = "TDDFT spectrum"
        elif "_nrixs" in name:
            kind = "NRIXS spectrum"
        elif name.endswith("_inp.txt"):
            kind = "input"
        out.append({
            "path": str(f),
            "size_bytes": f.stat().st_size,
            "kind_guess": kind,
        })
    return {"count": len(out), "files": out}
