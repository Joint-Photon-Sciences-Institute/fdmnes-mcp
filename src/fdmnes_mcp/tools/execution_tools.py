"""Async execution tools (mpirun fdmnes_mpi)."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from .. import config
from ..session import JobManager


# The JobManager is set by server.py via set_job_manager().
_JM: JobManager | None = None


def set_job_manager(jm: JobManager) -> None:
    global _JM
    _JM = jm


def _jm() -> JobManager:
    if _JM is None:
        raise RuntimeError("JobManager not initialised — server bug.")
    return _JM


def _have_mpirun() -> bool:
    return shutil.which("mpirun") is not None


async def fdmnes_run(
    working_dir: str | None = None,
    np: int | None = None,
    fdmfile: str | None = None,
    binary: str | None = None,
) -> dict[str, Any]:
    """Launch an FDMNES job in the background.

    Args:
      working_dir: directory containing the `fdmfile.txt` to run. Default:
        FDMNES_WORK_DIR from server config.
      np: number of MPI processes for `mpirun -np`. Default: 4.
      fdmfile: name of the master input file in `working_dir` (default:
        'fdmfile.txt'). FDMNES always reads this name; this argument lets
        you specify an alternate file that we'll symlink/copy in place.
      binary: override the FDMNES binary path. Default: server config.

    Returns: {job_id, status='running', cwd, cmd, pid, stdout_path,
    stderr_path}. Use `fdmnes_status(job_id)` to poll and
    `fdmnes_fetch_result(job_id)` once it completes.
    """
    cwd = Path(working_dir or config.FDMNES_WORK_DIR).expanduser().resolve()
    binp = Path(binary or config.FDMNES_BIN).expanduser().resolve()
    np_eff = int(np or config.FDMNES_MPI_DEFAULT_NP)

    if not binp.exists():
        return {"error": f"FDMNES binary not found at {binp}"}
    if not _have_mpirun():
        return {"error": "mpirun not found on PATH"}

    # If an alternate fdmfile is named, ensure cwd's fdmfile.txt matches it.
    if fdmfile and fdmfile != "fdmfile.txt":
        src = cwd / fdmfile
        dst = cwd / "fdmfile.txt"
        if not src.exists():
            return {"error": f"alternate fdmfile not found: {src}"}
        dst.write_text(src.read_text())

    if not (cwd / "fdmfile.txt").exists():
        return {"error": f"no fdmfile.txt in working directory {cwd}"}

    cmd = ["mpirun", "-np", str(np_eff), str(binp)]
    job = await _jm().launch(cmd, cwd=cwd, label="fdmnes")
    return {
        "job_id": job.job_id,
        "status": job.status,
        "cwd": job.cwd,
        "cmd": job.cmd,
        "pid": job.process.pid if job.process else None,
        "stdout_path": job.stdout_path,
        "stderr_path": job.stderr_path,
    }


def fdmnes_status(job_id: str, tail_n: int = 20) -> dict[str, Any]:
    """Poll the status of a running / completed FDMNES job.

    Args:
      job_id: ID returned by `fdmnes_run`.
      tail_n: how many trailing stdout lines to include.

    Returns: {job_id, status, wall_seconds, returncode (if completed),
    stdout_tail, stderr_tail}.
    """
    job = _jm().get(job_id)
    if not job:
        return {"error": f"unknown job_id '{job_id}'"}
    out = job.to_dict()
    out["stdout_tail"] = _jm().tail(job_id, "stdout", n_lines=tail_n)
    out["stderr_tail"] = _jm().tail(job_id, "stderr", n_lines=tail_n)
    return out


def fdmnes_list_jobs() -> dict[str, Any]:
    """List all jobs ever launched by this server (in-memory; no persistence)."""
    return {"jobs": _jm().list()}


async def fdmnes_cancel_job(job_id: str) -> dict[str, Any]:
    """Terminate a running FDMNES job.

    Args:
      job_id: ID returned by `fdmnes_run`.
    """
    cancelled = await _jm().cancel(job_id)
    return {"job_id": job_id, "cancelled": cancelled}


def fdmnes_fetch_result(job_id: str) -> dict[str, Any]:
    """Get a completed FDMNES job's results: status, exit code, output files.

    If the job is still running, returns its current state without scanning
    for outputs. Once complete, scans the working directory for files whose
    mtime is after the job start.

    Args:
      job_id: ID returned by `fdmnes_run`.
    """
    job = _jm().get(job_id)
    if not job:
        return {"error": f"unknown job_id '{job_id}'"}
    base = job.to_dict()
    if job.status == "running":
        base["note"] = "job still running; outputs not yet listed"
        return base
    # Walk the cwd for output files created during the run.
    cwd = Path(job.cwd)
    outputs: list[dict[str, Any]] = []
    start = job.started_at
    for f in cwd.rglob("*.txt"):
        try:
            st = f.stat()
        except FileNotFoundError:
            continue
        if st.st_mtime < start:
            continue
        if f.name.startswith("."):
            continue  # our own .stdout/.stderr
        outputs.append({
            "path": str(f),
            "size_bytes": st.st_size,
            "kind": "bav" if f.name.endswith("_bav.txt")
                else ("convolved" if "_conv" in f.name else "spectrum"),
        })
    base["outputs"] = outputs
    base["n_outputs"] = len(outputs)
    base["stdout_tail"] = _jm().tail(job_id, "stdout", n_lines=40)
    return base


async def fdmnes_run_example(example_name: str = "Cu", np: int | None = None) -> dict[str, Any]:
    """Smoke-test: run one of the bundled examples (Sim/Test_stand/in/*).

    Sets the bundle's `fdmfile.txt` to point at the requested example, then
    launches `mpirun fdmnes_mpi` from the bundle directory.

    Args:
      example_name: stem of the example, without `_inp.txt` (e.g. 'Cu',
        'Fe2O3_scf', 'Ni_mg'). Use `fdmnes_list_examples` to discover names.
      np: MPI rank count (default from server config).
    """
    bundle = Path(config.FDMNES_BUNDLE_DIR)
    inp = bundle / "Sim" / "Test_stand" / "in" / f"{example_name}_inp.txt"
    if not inp.exists():
        return {"error": f"example not found: {inp}"}
    (bundle / "fdmfile.txt").write_text(
        f"! launched by fdmnes-mcp\n 1\nSim/Test_stand/in/{example_name}_inp.txt\n"
    )
    return await fdmnes_run(working_dir=str(bundle), np=np)


async def fdmnes_reconvolve(
    source_prefix: str,
    output_prefix: str,
    *,
    gamma_max: float | None = None,
    gamma_hole: float | None = None,
    e_cut: float | None = None,
    ecent: float | None = None,
    elarg: float | None = None,
    gaussian: float | None = None,
    np: int = 1,
) -> dict[str, Any]:
    """Generate + run a convolution-only FDMNES job from an existing output.

    Creates a small `_inp.txt` that uses `Calculation <source_prefix>` to read
    the existing unconvolved spectrum and re-applies convolution with the
    requested parameters. Writes the convolution to `<output_prefix>_conv.txt`.

    Args:
      source_prefix: prefix (no extension) of the existing FDMNES output,
        e.g. 'Sim/Test_stand/Cu'. Must be resolvable from working dir.
      output_prefix: prefix for the re-convolved output.
      gamma_max, gamma_hole, e_cut, ecent, elarg, gaussian: convolution
        parameters. If None, FDMNES defaults are used.
      np: MPI rank count (1 is fine for pure convolution).
    """
    workdir = Path(source_prefix).parent or Path(".")
    workdir = workdir.resolve()
    if not workdir.exists():
        return {"error": f"working dir {workdir} doesn't exist"}

    lines = [
        "! convolution-only re-run generated by fdmnes-mcp",
        " Calculation",
        f"   {source_prefix}",
        " Conv_out",
        f"   {output_prefix}_conv.txt",
        " Convolution",
    ]
    if gamma_max is not None:
        lines += [" Gamma_max", f"   {gamma_max}"]
    if gamma_hole is not None:
        lines += [" Gamma_hole", f"   {gamma_hole}"]
    if e_cut is not None:
        lines += [" E_cut", f"   {e_cut}"]
    if ecent is not None:
        lines += [" Ecent", f"   {ecent}"]
    if elarg is not None:
        lines += [" Elarg", f"   {elarg}"]
    if gaussian is not None:
        lines += [" Gaussian", f"   {gaussian}"]
    lines += [" End", ""]

    inp_path = workdir / "_reconvolve_inp.txt"
    inp_path.write_text("\n".join(lines))

    fdmfile = "! convolution-only job\n 1\n_reconvolve_inp.txt\n"
    (workdir / "fdmfile.txt").write_text(fdmfile)

    return await fdmnes_run(working_dir=str(workdir), np=np)
