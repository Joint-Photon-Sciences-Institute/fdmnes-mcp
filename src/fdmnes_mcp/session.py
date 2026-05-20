"""
Session / job manager for async FDMNES runs.

Each job is launched as a detached `mpirun ./fdmnes_mpi` subprocess; the
JobManager keeps a record (job_id, pid, cwd, start_time, status, returncode,
stdout/stderr file paths). Tools query / update jobs by job_id.
"""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Job:
    job_id: str
    cwd: str
    cmd: list[str]
    started_at: float
    stdout_path: str
    stderr_path: str
    status: str = "running"  # running | completed | failed | not_found
    returncode: int | None = None
    finished_at: float | None = None
    # Not serialised:
    process: Any = field(default=None, repr=False)

    def to_dict(self) -> dict:
        # Build manually — asdict() deep-copies fields, which fails on the
        # asyncio subprocess (contains a non-picklable _contextvars.Context).
        return {
            "job_id": self.job_id,
            "cwd": self.cwd,
            "cmd": list(self.cmd),
            "started_at": self.started_at,
            "stdout_path": self.stdout_path,
            "stderr_path": self.stderr_path,
            "status": self.status,
            "returncode": self.returncode,
            "finished_at": self.finished_at,
            "wall_seconds": (self.finished_at or time.time()) - self.started_at,
        }


class JobManager:
    """In-memory job registry. Jobs are cleaned up only when the server stops."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    # ---- lifecycle ----------------------------------------------------

    async def launch(self, cmd: list[str], cwd: Path, label: str | None = None) -> Job:
        """Spawn the given command in cwd. Returns the new Job immediately."""
        cwd = Path(cwd).resolve()
        cwd.mkdir(parents=True, exist_ok=True)

        job_id = (label or "job") + "-" + uuid.uuid4().hex[:8]
        stdout_path = cwd / f".{job_id}.stdout"
        stderr_path = cwd / f".{job_id}.stderr"

        # Open log files for streaming; subprocess will inherit fds.
        stdout_fh = open(stdout_path, "wb")
        stderr_fh = open(stderr_path, "wb")
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=str(cwd), stdout=stdout_fh, stderr=stderr_fh,
        )

        job = Job(
            job_id=job_id,
            cwd=str(cwd),
            cmd=list(cmd),
            started_at=time.time(),
            stdout_path=str(stdout_path),
            stderr_path=str(stderr_path),
            process=proc,
        )
        self._jobs[job_id] = job

        # Background reaper: when the process finishes, update status.
        asyncio.create_task(self._reap(job, stdout_fh, stderr_fh))
        return job

    async def _reap(self, job: Job, *fhs) -> None:
        rc = await job.process.wait()
        for fh in fhs:
            try:
                fh.close()
            except Exception:
                pass
        job.returncode = rc
        job.finished_at = time.time()
        job.status = "completed" if rc == 0 else "failed"

    # ---- queries ------------------------------------------------------

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def list(self) -> list[dict]:
        return [j.to_dict() for j in self._jobs.values()]

    def tail(self, job_id: str, kind: str = "stdout", n_lines: int = 30) -> str:
        job = self.get(job_id)
        if not job:
            return ""
        path = Path(job.stdout_path if kind == "stdout" else job.stderr_path)
        if not path.exists():
            return ""
        # Read efficiently from the tail.
        with open(path, "rb") as f:
            try:
                f.seek(-min(8192, path.stat().st_size), 2)
            except OSError:
                f.seek(0)
            data = f.read().decode("utf-8", errors="replace")
        return "\n".join(data.splitlines()[-n_lines:])

    # ---- cleanup ------------------------------------------------------

    async def cancel(self, job_id: str) -> bool:
        job = self.get(job_id)
        if not job or job.status != "running":
            return False
        try:
            job.process.terminate()
            try:
                await asyncio.wait_for(job.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                job.process.kill()
                await job.process.wait()
        except ProcessLookupError:
            pass
        job.status = "failed"
        job.returncode = -1
        job.finished_at = time.time()
        return True
