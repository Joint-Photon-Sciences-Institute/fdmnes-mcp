"""
Paths and defaults for fdmnes-mcp.

The server tries hard to find a usable FDMNES binary and examples directory
without any user configuration. If autodetection fails, set the relevant
environment variable before launching the MCP server.

Environment variables (all optional):

  FDMNES_BIN              Absolute path to the FDMNES binary (parallel or
                          serial). If unset, we search $PATH for
                          'fdmnes_mpi', 'fdmnes_linux_parallel', 'fdmnes',
                          'fdmnes_linux', then a few common install
                          locations.

  FDMNES_BUNDLE_DIR       Directory containing the standard FDMNES bundle
                          layout: 'fdmfile.txt' + 'Sim/Test_stand/'. Used
                          by `fdmnes_run_example`. If unset, we search a
                          few common locations.

  FDMNES_EXAMPLES_DIR     Directory of '*_inp.txt' example inputs.
                          Defaults to '<FDMNES_BUNDLE_DIR>/Sim/Test_stand/in'.

  FDMNES_DOCS_DIR         External docs directory (markdown). If set,
                          overrides the docs we ship in the package itself.

  FDMNES_WORK_DIR         Default working directory for new jobs. Defaults
                          to '~/fdmnes-jobs'.

  FDMNES_MPI_DEFAULT_NP   Default '-np' for mpirun. Defaults to 4.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path


# ---- Binary detection ----------------------------------------------------

_BINARY_CANDIDATES = (
    "fdmnes_mpi",
    "fdmnes_linux_parallel",
    "fdmnes",
    "fdmnes_linux",
    "fdmnes_linux_serial",
)

_COMMON_INSTALL_DIRS = (
    "~/fdmnes",
    "~/FDMNES",
    "~/.local/share/fdmnes",
    "/opt/fdmnes",
    "/usr/local/fdmnes",
    "/usr/local/bin",
)


def _detect_binary() -> Path | None:
    """Find the FDMNES binary. None if nothing plausible turns up."""
    env = os.environ.get("FDMNES_BIN")
    if env:
        return Path(env).expanduser()

    # 1) On $PATH
    for name in _BINARY_CANDIDATES:
        hit = shutil.which(name)
        if hit:
            return Path(hit)

    # 2) Common install directories
    for d in _COMMON_INSTALL_DIRS:
        base = Path(d).expanduser()
        if not base.exists():
            continue
        for name in _BINARY_CANDIDATES:
            cand = base / name
            if cand.is_file() and os.access(cand, os.X_OK):
                return cand
            # Nested layouts (e.g. ~/fdmnes/parallel_bundle/.../fdmnes_linux_parallel)
            for nested in base.rglob(name):
                if nested.is_file() and os.access(nested, os.X_OK):
                    return nested

    return None


def _detect_bundle_dir() -> Path | None:
    """Find a directory laid out like the upstream FDMNES Linux bundle."""
    env = os.environ.get("FDMNES_BUNDLE_DIR")
    if env:
        return Path(env).expanduser()

    candidates = (
        "~/fdmnes/linux_bundle/fdmnes_Linux",
        "~/FDMNES/linux_bundle/fdmnes_Linux",
        "/opt/fdmnes/linux_bundle/fdmnes_Linux",
    )
    for d in candidates:
        p = Path(d).expanduser()
        if (p / "fdmfile.txt").exists():
            return p

    # Look for `Sim/Test_stand` near the binary
    bin_ = _detect_binary()
    if bin_:
        for parent in [bin_.parent, *bin_.parents]:
            if (parent / "fdmfile.txt").exists() and (parent / "Sim" / "Test_stand").is_dir():
                return parent
            if (parent / "Sim" / "Test_stand").is_dir():
                return parent
    return None


# ---- Packaged docs -------------------------------------------------------

def _packaged_docs_dir() -> Path:
    """The 'data/docs' folder we ship inside this package."""
    return Path(__file__).resolve().parent / "data" / "docs"


# ---- Resolved values -----------------------------------------------------

_bin = _detect_binary()
FDMNES_BIN: Path = _bin if _bin else Path("fdmnes_mpi")  # placeholder if not found

_bundle = _detect_bundle_dir()
FDMNES_BUNDLE_DIR: Path = _bundle if _bundle else Path("")

FDMNES_EXAMPLES_DIR: Path = Path(os.environ.get(
    "FDMNES_EXAMPLES_DIR",
    str(FDMNES_BUNDLE_DIR / "Sim" / "Test_stand" / "in") if _bundle else "",
)).expanduser()

# Docs: packaged-by-default, env-override-permitted.
_env_docs = os.environ.get("FDMNES_DOCS_DIR")
FDMNES_DOCS_DIR: Path = (
    Path(_env_docs).expanduser() if _env_docs else _packaged_docs_dir()
)

FDMNES_WORK_DIR: Path = Path(
    os.environ.get("FDMNES_WORK_DIR", "~/fdmnes-jobs")
).expanduser()

FDMNES_MPI_DEFAULT_NP: int = int(os.environ.get("FDMNES_MPI_DEFAULT_NP", "4"))


def summary() -> dict:
    """Snapshot of current configuration. Shown by `--info`."""
    return {
        "fdmnes_bin": str(FDMNES_BIN),
        "fdmnes_bin_exists": FDMNES_BIN.exists(),
        "fdmnes_bin_executable": FDMNES_BIN.exists() and os.access(FDMNES_BIN, os.X_OK),
        "bundle_dir": str(FDMNES_BUNDLE_DIR) if FDMNES_BUNDLE_DIR else None,
        "bundle_dir_exists": bool(FDMNES_BUNDLE_DIR) and FDMNES_BUNDLE_DIR.exists(),
        "examples_dir": str(FDMNES_EXAMPLES_DIR) if FDMNES_EXAMPLES_DIR else None,
        "examples_dir_exists": bool(FDMNES_EXAMPLES_DIR) and FDMNES_EXAMPLES_DIR.exists(),
        "docs_dir": str(FDMNES_DOCS_DIR),
        "docs_dir_exists": FDMNES_DOCS_DIR.exists(),
        "docs_source": "env" if _env_docs else "packaged",
        "work_dir": str(FDMNES_WORK_DIR),
        "default_np": FDMNES_MPI_DEFAULT_NP,
    }


def info_text() -> str:
    """Human-readable 'is everything wired up correctly' report."""
    s = summary()
    lines = ["fdmnes-mcp configuration", "========================", ""]
    lines.append(f"  FDMNES binary       : {s['fdmnes_bin']}")
    lines.append(f"      exists / x-bit  : {s['fdmnes_bin_exists']} / {s['fdmnes_bin_executable']}")
    lines.append(f"  Bundle directory    : {s['bundle_dir']}")
    lines.append(f"      exists          : {s['bundle_dir_exists']}")
    lines.append(f"  Examples directory  : {s['examples_dir']}")
    lines.append(f"      exists          : {s['examples_dir_exists']}")
    lines.append(f"  Docs directory      : {s['docs_dir']}  ({s['docs_source']})")
    lines.append(f"      exists          : {s['docs_dir_exists']}")
    lines.append(f"  Work directory      : {s['work_dir']}")
    lines.append(f"  mpirun default -np  : {s['default_np']}")
    lines.append("")
    issues = []
    if not s["fdmnes_bin_exists"]:
        issues.append(
            "  [!] FDMNES binary not found. Set FDMNES_BIN=/abs/path/to/fdmnes_mpi\n"
            "      before launching the MCP server, OR place fdmnes_mpi on $PATH."
        )
    elif not s["fdmnes_bin_executable"]:
        issues.append(
            f"  [!] FDMNES binary at {s['fdmnes_bin']} is not executable.\n"
            f"      Run: chmod +x {s['fdmnes_bin']}"
        )
    if not s["bundle_dir_exists"]:
        issues.append(
            "  [.] No bundled examples found. fdmnes_run_example will not\n"
            "      work. Download the Linux bundle from\n"
            "      https://fdmnes.neel.cnrs.fr/ and set FDMNES_BUNDLE_DIR."
        )
    if not s["docs_dir_exists"]:
        issues.append(
            "  [.] No docs directory found. fdmnes_keyword_lookup will fall\n"
            "      back to a minimal hand-coded DB."
        )
    if issues:
        lines.append("Issues:")
        lines.extend(issues)
    else:
        lines.append("All paths resolved.")
    return "\n".join(lines)
