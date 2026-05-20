# fdmnes-mcp

[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-server-purple.svg)](https://modelcontextprotocol.io)

MCP (Model Context Protocol) server that wraps **FDMNES** — the ab-initio Fortran code for X-ray spectroscopy by Yves Joly at Institut Néel CNRS, Grenoble. Drive FDMNES through **Claude Desktop**, **Claude Code**, **Codex CLI**, **Cline**, or any other MCP-aware client with natural-language tool calls.

Build and validate input files, launch parallel `mpirun fdmnes_mpi` jobs asynchronously, poll status, fetch outputs, plot spectra, and look up any of FDMNES's ~350 input keywords from a source-grounded catalog — without ever leaving the chat.

> **About FDMNES.** FDMNES (Finite Difference Method Near Edge Structure) computes XANES, EXAFS (via the FDMX extension), XMCD, RXS/DAFS, RIXS, NRIXS / X-Raman, optic, and emission spectra. Two solver engines: a 3D real-space finite-difference solver (full-potential) and a multiple-scattering Green's function (muffin-tin). Free download at <https://fdmnes.neel.cnrs.fr/>. This wrapper does NOT redistribute FDMNES itself — you install FDMNES separately.

---

## Install

### 1. Install FDMNES

If you haven't already, grab FDMNES from <https://fdmnes.neel.cnrs.fr/download/>. You want either:

- the **parallel Linux executable** (`parallel_fdmnes` zip — recommended), or
- the **Fortran source** + the MUMPS / ScaLAPACK / OpenMPI toolchain (build it yourself).

Make sure your FDMNES binary is executable (`chmod +x <binary>`) and ideally on `$PATH`. The MCP server autodetects it from `$PATH`, then from common install directories (`~/fdmnes`, `~/FDMNES`, `/opt/fdmnes`, `/usr/local/fdmnes`); override with the `FDMNES_BIN` env var if needed.

### 2. Install fdmnes-mcp

From PyPI (recommended once a release is published):

```bash
pip install fdmnes-mcp
```

From GitHub `main` (bleeding edge):

```bash
pip install git+https://github.com/Joint-Photon-Sciences-Institute/fdmnes-mcp.git
```

From a local checkout (for development):

```bash
git clone https://github.com/Joint-Photon-Sciences-Institute/fdmnes-mcp.git
cd fdmnes-mcp
python3 -m venv .venv
.venv/bin/pip install -e .
```

After install, the `fdmnes-mcp` console script is on your `$PATH` and equivalent to `python -m fdmnes_mcp`.

### 3. Verify the wiring

```bash
fdmnes-mcp --info     # or: python -m fdmnes_mcp --info
```

Prints the resolved paths and flags anything missing. Example output:

```
fdmnes-mcp configuration
========================

  FDMNES binary       : /usr/local/bin/fdmnes_mpi
      exists / x-bit  : True / True
  Bundle directory    : /opt/fdmnes/linux_bundle/fdmnes_Linux
      exists          : True
  Examples directory  : /opt/fdmnes/linux_bundle/fdmnes_Linux/Sim/Test_stand/in
      exists          : True
  Docs directory      : /.../site-packages/fdmnes_mcp/data/docs  (packaged)
      exists          : True
  Work directory      : /home/you/fdmnes-jobs
  mpirun default -np  : 4

All paths resolved.
```

---

## Register with your MCP client

### Claude Code

```bash
claude mcp add fdmnes -- fdmnes-mcp
```

(If `fdmnes-mcp` isn't on your `$PATH`, use the absolute path returned by `which fdmnes-mcp`.)

### Claude Desktop

Edit `claude_desktop_config.json` (location varies by OS: `~/Library/Application Support/Claude/` on macOS, `%APPDATA%\Claude\` on Windows, `~/.config/Claude/` on Linux):

```json
{
  "mcpServers": {
    "fdmnes": {
      "command": "fdmnes-mcp"
    }
  }
}
```

To override defaults via environment variables:

```json
{
  "mcpServers": {
    "fdmnes": {
      "command": "fdmnes-mcp",
      "env": {
        "FDMNES_BIN": "/opt/fdmnes/fdmnes_mpi",
        "FDMNES_MPI_DEFAULT_NP": "8"
      }
    }
  }
}
```

### Codex CLI

In your `~/.codex/config.toml`:

```toml
[mcp_servers.fdmnes]
command = "fdmnes-mcp"
```

### Cline (VS Code)

Edit `cline_mcp_settings.json` (Cline → MCP Servers → Configure):

```json
{
  "mcpServers": {
    "fdmnes": {
      "command": "fdmnes-mcp",
      "transport": "stdio"
    }
  }
}
```

### Any generic MCP client

Run the binary as a stdio server:

```bash
fdmnes-mcp
```

---

## Quick start (Claude)

After registering, try:

> List the bundled FDMNES examples, then run the Cu K-edge one on 4 ranks and plot the convolved spectrum when it finishes.

Claude will call (roughly):

1. `fdmnes_list_examples` → see `Cu`
2. `fdmnes_run_example(example_name="Cu", np=4)` → get a `job_id`
3. `fdmnes_status(job_id)` until `status == "completed"`
4. `fdmnes_fetch_result(job_id)` → returns output paths
5. `fdmnes_plot_spectrum(path=".../Cu_conv.txt")` → renders the spectrum

Or for a new material:

> Scaffold an SCF XANES job for Fe₂O₃ at the Fe K-edge with Hubbard U = 5 eV under `~/jobs/fe2o3/`, then run it on 8 ranks.

---

## Configuration

All paths are auto-detected with sensible fallbacks. Override any of them via environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `FDMNES_BIN` | autodetect from `$PATH` and common installs | FDMNES binary (parallel or serial) |
| `FDMNES_BUNDLE_DIR` | autodetect | Directory with `fdmfile.txt` + `Sim/Test_stand/` |
| `FDMNES_EXAMPLES_DIR` | `$FDMNES_BUNDLE_DIR/Sim/Test_stand/in` | Bundled `_inp.txt` examples |
| `FDMNES_DOCS_DIR` | packaged docs | Override path to docs (keyword DB source) |
| `FDMNES_WORK_DIR` | `~/fdmnes-jobs` | Default cwd for new jobs |
| `FDMNES_MPI_DEFAULT_NP` | `4` | Default `-np` for `mpirun` |

Call `fdmnes_get_config` inside a Claude session at any time to see what's currently active.

---

## Tool reference

**27 tools across 6 categories** (+ 8 resources). See [`src/fdmnes_mcp/tools/`](src/fdmnes_mcp/tools/) for implementations.

### I/O & inspection

| Tool | Purpose |
|---|---|
| `fdmnes_get_config` | Show MCP paths + binary status |
| `fdmnes_list_examples` | List bundled `_inp.txt` examples |
| `fdmnes_read_input` | Parse an `_inp.txt` into structured blocks |
| `fdmnes_read_spectrum` | Read `X.txt` / `X_conv.txt` into arrays (auto-downsampled) |
| `fdmnes_summarise_spectrum` | Compact metadata-only view (no arrays) |
| `fdmnes_read_bav` | Extract release / point group / Symsite / SCF trace / Fermi level / parallel banner from a `_bav.txt` |
| `fdmnes_list_outputs` | List FDMNES output files under a prefix or directory |

### Authoring

| Tool | Purpose |
|---|---|
| `fdmnes_keyword_lookup` | Look up a keyword (name or alias) → args, default, effect, source ref |
| `fdmnes_keyword_search` | Substring search across name / alias / effect text |
| `fdmnes_list_keyword_categories` | List the ~16 categories in the keyword DB |
| `fdmnes_validate_input` | Lint an `_inp.txt` against the keyword catalog |
| `fdmnes_build_input` | Build an `_inp.txt` from structured params |

### Execution (async)

| Tool | Purpose |
|---|---|
| `fdmnes_run` | Launch `mpirun fdmnes` in the background → returns a `job_id` |
| `fdmnes_run_example` | One-shot: select a bundled example by name and launch |
| `fdmnes_status` | Poll job status + stdout/stderr tails |
| `fdmnes_list_jobs` | List all jobs launched in this session |
| `fdmnes_cancel_job` | Terminate a running job |
| `fdmnes_fetch_result` | Once a job completes, list its output files |
| `fdmnes_reconvolve` | Generate + run a convolution-only job that re-broadens an existing output |

### Plotting

| Tool | Purpose |
|---|---|
| `fdmnes_plot_spectrum` | Render an FDMNES output to PNG (base64 + optional save path) |
| `fdmnes_compare_spectra` | Overlay multiple spectra with optional normalisation |

### Workflow templates

| Tool | Purpose |
|---|---|
| `fdmnes_template_xanes` | Scaffold a basic XANES job (FDM or MS) |
| `fdmnes_template_scf_xanes` | XANES with SCF (and optional Hubbard U) |
| `fdmnes_template_fdmx_exafs` | EXAFS via FDMX (K-edge) |
| `fdmnes_template_rxs` | Resonant diffraction with one or more reflections |
| `fdmnes_template_xmcd` | Magnetic / XMCD with circular polarisation |

### Escape hatch

| Tool | Purpose |
|---|---|
| `fdmnes_run_shell` | Run any shell command in the FDMNES workspace (sparingly) |

## Resources

Read-only docs available at:

| URI | Content |
|---|---|
| `fdmnes://config` | Server config snapshot |
| `fdmnes://docs/methods` | FDM vs MST, DFT/TDDFT, defaults |
| `fdmnes://docs/io` | Input / output file structure |
| `fdmnes://docs/keywords` | Full keyword reference (large) |
| `fdmnes://docs/pipelines` | 16 workflow recipes |
| `fdmnes://docs/examples` | Annotated catalog of bundled inputs |
| `fdmnes://docs/keyword/{name}` | Reference card for a single keyword |

---

## Architecture

```
src/fdmnes_mcp/
├── __main__.py                # entry point with --info / --help / --version
├── server.py                  # FastMCP setup + tool/resource registration
├── config.py                  # autodetection + env-var-driven paths
├── session.py                 # JobManager (asyncio subprocess registry)
├── parsers/
│   ├── input_parser.py        # _inp.txt → structured blocks
│   ├── spectrum_parser.py     # X.txt / X_conv.txt → numpy arrays
│   ├── bav_parser.py          # _bav.txt → highlights
│   └── keyword_db.py          # ~770-entry keyword DB (mined from packaged docs)
├── tools/
│   ├── io_tools.py
│   ├── authoring_tools.py
│   ├── execution_tools.py     # async run / status / fetch
│   ├── plot_tools.py
│   ├── template_tools.py      # workflow one-shots
│   └── shell_tools.py
├── resources/docs.py          # fdmnes:// resource URIs
└── data/docs/                 # packaged reference docs (markdown)
```

The keyword DB is mined from the shipped `data/docs/keyword-reference.md` at server startup. Override with `FDMNES_DOCS_DIR` to point at a different docs tree (e.g. a forked / extended catalog).

---

## Citing FDMNES

If you publish results obtained with FDMNES (with or without this wrapper), the FDMNES author asks that you cite the following, as listed in the FDMNES User's Guide:

- **Main FDMNES paper**: O. Bunau and Y. Joly, *J. Phys.: Condens. Matter* **21**, 345501 (2009).
- **MUMPS-accelerated FDM**: S. A. Guda et al., *J. Chem. Theory Comput.* **11**, 4512-4521 (2015).
- **FDMX EXAFS extension**: J. D. Bourke, C. T. Chantler, Y. Joly, *J. Synchrotron Rad.* **23**, 551-559 (2016).
- **Surface RXD**: Y. Joly et al., *J. Chem. Theory Comput.* **14**, 973-980 (2018).
- **X-Raman / NRIXS**: Y. Joly, C. Cavallari, S. A. Guda, C. J. Sahle, *J. Chem. Theory Comput.* **13**, 2172-2177 (2017).
- **International Tables for Crystallography**, Volume I (2021, 2022).

This wrapper does not need a separate citation, but a link or acknowledgement is appreciated:
> *FDMNES jobs were driven through the fdmnes-mcp wrapper (Joint Photon Sciences Institute, https://github.com/Joint-Photon-Sciences-Institute/fdmnes-mcp).*

---

## Contributing & releases

Issues and pull requests welcome at <https://github.com/Joint-Photon-Sciences-Institute/fdmnes-mcp>.

**Release process** (for maintainers):

1. Bump `version` in `pyproject.toml`.
2. Commit, tag (`git tag v0.x.y`), push the tag (`git push --tags`).
3. The `Publish to PyPI` GitHub Actions workflow builds and publishes via [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/). No API tokens needed in the repo — the project's PyPI page must be configured to trust this repo + workflow on first release (one-time setup).

## License

This wrapper is released under the [BSD 3-Clause License](LICENSE). FDMNES itself is independent software with its own distribution terms; see <https://fdmnes.neel.cnrs.fr/> for FDMNES licensing questions.

## Acknowledgements

Built in the style of [xraylarch-mcp](https://github.com/Joint-Photon-Sciences-Institute/xraylarch-mcp). Thanks to Yves Joly and the FDMNES developers for making the code freely available, and to the MCP / FastMCP authors for the protocol that makes wrappers like this trivial.
