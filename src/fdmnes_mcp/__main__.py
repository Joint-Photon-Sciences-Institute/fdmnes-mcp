"""
Entry point: `python -m fdmnes_mcp [--info]`.

By default starts the MCP stdio server. Pass --info to print the resolved
configuration and exit (useful for diagnosing where FDMNES is installed).
"""
from __future__ import annotations

import sys


def _print_info() -> int:
    from . import config
    print(config.info_text())
    return 0 if config.summary()["fdmnes_bin_exists"] else 1


def main() -> None:
    if "--info" in sys.argv[1:] or "info" in sys.argv[1:]:
        raise SystemExit(_print_info())
    if "--version" in sys.argv[1:] or "-V" in sys.argv[1:]:
        from . import __version__
        print(f"fdmnes-mcp {__version__}")
        raise SystemExit(0)
    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        print(
            "fdmnes-mcp — MCP server wrapping FDMNES.\n\n"
            "Usage:\n"
            "  python -m fdmnes_mcp           Start the MCP stdio server\n"
            "  python -m fdmnes_mcp --info    Show resolved configuration\n"
            "  python -m fdmnes_mcp --version Print version\n"
            "  python -m fdmnes_mcp --help    This message\n\n"
            "Environment variables (all optional):\n"
            "  FDMNES_BIN, FDMNES_BUNDLE_DIR, FDMNES_EXAMPLES_DIR,\n"
            "  FDMNES_DOCS_DIR, FDMNES_WORK_DIR, FDMNES_MPI_DEFAULT_NP\n"
        )
        raise SystemExit(0)
    from .server import main as server_main
    server_main()


if __name__ == "__main__":
    main()
