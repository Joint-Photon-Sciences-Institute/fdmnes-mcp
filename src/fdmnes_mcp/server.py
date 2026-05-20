"""
fdmnes-mcp — MCP server wrapping FDMNES for X-ray spectroscopy simulation.

Stdio transport. Claude Code launches this as `python -m fdmnes_mcp` per the
MCP server registration (`claude mcp add fdmnes -- ...`).

Tool families:
  io          — list_examples, read_input, read_spectrum, read_bav, list_outputs
  authoring   — build_input, validate_input, keyword_lookup, keyword_search
  execution   — run, run_example, status, fetch_result, cancel, reconvolve
  plot        — plot_spectrum, compare_spectra
  templates   — xanes, scf_xanes, fdmx_exafs, rxs, xmcd
  shell       — run_shell (escape hatch)

Resources: docs (markdown), config snapshot, per-keyword cards at
  fdmnes://docs/*, fdmnes://config, fdmnes://docs/keyword/{name}.
"""
from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

from .session import JobManager
from .tools import (
    io_tools,
    authoring_tools,
    execution_tools,
    plot_tools,
    template_tools,
    shell_tools,
)
from .resources import docs as docs_resources


logging.basicConfig(
    format="%(asctime)s %(levelname)s fdmnes-mcp | %(message)s",
    level=logging.INFO,
    stream=sys.stderr,
)
log = logging.getLogger("fdmnes-mcp")


mcp = FastMCP(
    "fdmnes",
    instructions=(
        "FDMNES MCP server. Drive FDMNES (X-ray spectroscopy ab-initio code) "
        "via natural language: list/inspect bundled examples, build input "
        "files from templates (xanes, scf_xanes, fdmx_exafs, rxs, xmcd), "
        "launch jobs (`fdmnes_run` / `fdmnes_run_example`), poll status, "
        "fetch results, and plot spectra. Use the docs resources at "
        "fdmnes://docs/* for the comprehensive reference."
    ),
)


# Job manager — shared across execution tools
job_manager = JobManager()
execution_tools.set_job_manager(job_manager)


# ---------- register tools ------------------------------------------------

# IO
for fn in (
    io_tools.fdmnes_get_config,
    io_tools.fdmnes_list_examples,
    io_tools.fdmnes_read_input,
    io_tools.fdmnes_read_spectrum,
    io_tools.fdmnes_summarise_spectrum,
    io_tools.fdmnes_read_bav,
    io_tools.fdmnes_list_outputs,
):
    mcp.add_tool(fn)

# Authoring
for fn in (
    authoring_tools.fdmnes_keyword_lookup,
    authoring_tools.fdmnes_keyword_search,
    authoring_tools.fdmnes_list_keyword_categories,
    authoring_tools.fdmnes_validate_input,
    authoring_tools.fdmnes_build_input,
):
    mcp.add_tool(fn)

# Execution
for fn in (
    execution_tools.fdmnes_run,
    execution_tools.fdmnes_run_example,
    execution_tools.fdmnes_status,
    execution_tools.fdmnes_list_jobs,
    execution_tools.fdmnes_cancel_job,
    execution_tools.fdmnes_fetch_result,
    execution_tools.fdmnes_reconvolve,
):
    mcp.add_tool(fn)

# Plotting
for fn in (
    plot_tools.fdmnes_plot_spectrum,
    plot_tools.fdmnes_compare_spectra,
):
    mcp.add_tool(fn)

# Workflow templates
for fn in (
    template_tools.fdmnes_template_xanes,
    template_tools.fdmnes_template_scf_xanes,
    template_tools.fdmnes_template_fdmx_exafs,
    template_tools.fdmnes_template_rxs,
    template_tools.fdmnes_template_xmcd,
):
    mcp.add_tool(fn)

# Shell escape hatch
mcp.add_tool(shell_tools.fdmnes_run_shell)


# ---------- register resources --------------------------------------------

docs_resources.register_resources(mcp)


# ---------- entry point ---------------------------------------------------

def main() -> None:
    """Run the MCP server over stdio."""
    log.info("fdmnes-mcp starting")
    mcp.run()


if __name__ == "__main__":
    main()
