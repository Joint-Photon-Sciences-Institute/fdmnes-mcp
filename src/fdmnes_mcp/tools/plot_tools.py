"""Plotting tools — render FDMNES spectra to PNG and return the image."""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from ..parsers import spectrum_parser


def _save_png(fig: plt.Figure, save_to: str | None) -> dict[str, Any]:
    """Save the figure and return {path?, png_bytes_b64}."""
    out: dict[str, Any] = {}
    if save_to:
        p = Path(save_to)
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=120, bbox_inches="tight")
        out["path"] = str(p)
    # Also return base64 for inline display
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    out["png_bytes_b64"] = base64.b64encode(buf.getvalue()).decode("ascii")
    out["width_in"], out["height_in"] = fig.get_size_inches().tolist()
    plt.close(fig)
    return out


def fdmnes_plot_spectrum(
    path: str,
    column: str | None = None,
    save_to: str | None = None,
    title: str | None = None,
    log_y: bool = False,
) -> dict[str, Any]:
    """Plot an FDMNES spectrum file.

    Args:
      path: path to a FDMNES output (.txt or _conv.txt).
      column: which data column to plot vs energy. Default: the second column
        (typically <xanes>). Use 'fdmnes_read_spectrum' to see available
        columns.
      save_to: if given, save the PNG to this path.
      title: figure title. Default: file name.
      log_y: log-scale the y-axis.

    Returns: {path?, png_bytes_b64, width_in, height_in, plotted_column,
    energy_range}.
    """
    p = Path(path)
    if not p.exists():
        return {"error": f"file not found: {p}"}
    parsed = spectrum_parser.parse_spectrum(p)
    if not parsed.get("data"):
        return {"error": parsed.get("error", "no data in file")}
    cols = parsed["columns"]
    if not cols:
        return {"error": "no columns identified"}
    ekey = cols[0]
    e = parsed["data"][ekey]
    ckey = column if column else (cols[1] if len(cols) > 1 else cols[0])
    if ckey not in parsed["data"]:
        return {"error": f"column '{ckey}' not in file. Available: {cols}"}
    y = parsed["data"][ckey]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(e, y, lw=1.5)
    ax.set_xlabel(f"{ekey} (eV)")
    ax.set_ylabel(ckey)
    if log_y:
        ax.set_yscale("log")
    ax.set_title(title or p.name)
    ax.grid(alpha=0.3)
    out = _save_png(fig, save_to)
    out["plotted_column"] = ckey
    out["energy_range"] = [float(e[0]), float(e[-1])]
    return out


def fdmnes_compare_spectra(
    paths: list[str],
    labels: list[str] | None = None,
    column: str | None = None,
    save_to: str | None = None,
    title: str | None = None,
    normalize: bool = False,
) -> dict[str, Any]:
    """Overlay-plot multiple FDMNES spectra.

    Args:
      paths: list of FDMNES output file paths to overlay.
      labels: optional list of labels (same length as paths). Default: file
        basenames.
      column: which column to plot. Default: 2nd column of the first file.
      save_to: PNG output path.
      title: figure title.
      normalize: if True, scale each curve to [0, 1] over the plotted column.

    Returns: {path?, png_bytes_b64, plotted_column, n_curves}.
    """
    if not paths:
        return {"error": "no paths given"}
    if labels and len(labels) != len(paths):
        return {"error": "labels length must equal paths length"}
    fig, ax = plt.subplots(figsize=(8, 5))
    chosen_col = None
    n_plotted = 0
    for i, raw in enumerate(paths):
        p = Path(raw)
        if not p.exists():
            continue
        parsed = spectrum_parser.parse_spectrum(p)
        cols = parsed["columns"]
        if not cols:
            continue
        ekey = cols[0]
        ckey = column if column else (cols[1] if len(cols) > 1 else cols[0])
        if ckey not in parsed["data"]:
            continue
        e = parsed["data"][ekey]
        y = parsed["data"][ckey]
        if normalize:
            y = np.array(y)
            r = (y.max() - y.min()) or 1.0
            y = (y - y.min()) / r
        label = labels[i] if labels else p.name
        ax.plot(e, y, label=label, lw=1.5)
        chosen_col = ckey
        n_plotted += 1
    ax.set_xlabel("Energy (eV)")
    ax.set_ylabel(chosen_col or "value")
    ax.set_title(title or "FDMNES spectra comparison")
    ax.legend(fontsize=9, loc="best")
    ax.grid(alpha=0.3)
    out = _save_png(fig, save_to)
    out["plotted_column"] = chosen_col
    out["n_curves"] = n_plotted
    return out
