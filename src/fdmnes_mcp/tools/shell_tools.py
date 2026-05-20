"""Escape hatch — arbitrary shell commands in the FDMNES workspace."""
from __future__ import annotations

import asyncio
import shlex
from pathlib import Path
from typing import Any

from .. import config


async def fdmnes_run_shell(
    command: str,
    working_dir: str | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    """Run an arbitrary shell command. ESCAPE HATCH — use sparingly.

    For any FDMNES operation not covered by a dedicated tool. Useful for
    one-off `ls`, `cat`, gnuplot, postprocessing.

    Args:
      command: the shell command line (no shell substitution; runs through
        /bin/sh -c).
      working_dir: cwd for the command. Default: server work dir.
      timeout: seconds before killing the subprocess.

    Returns: {exit_code, stdout, stderr, timed_out}.
    """
    cwd = Path(working_dir or config.FDMNES_WORK_DIR).expanduser().resolve()
    cwd.mkdir(parents=True, exist_ok=True)
    proc = await asyncio.create_subprocess_shell(
        command, cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        timed_out = False
    except asyncio.TimeoutError:
        proc.kill()
        stdout, stderr = await proc.communicate()
        timed_out = True
    return {
        "exit_code": proc.returncode,
        "stdout": stdout.decode("utf-8", errors="replace")[-8192:],
        "stderr": stderr.decode("utf-8", errors="replace")[-4096:],
        "timed_out": timed_out,
        "cwd": str(cwd),
    }
