"""
Lightweight parser for FDMNES `_inp.txt` job files.

Format (recap):
- Line-oriented, free-form, case-insensitive.
- Comments start with '!'. Blank lines ignored.
- A "block" is a keyword on its own line, followed by 0+ value lines.
- Reading stops at the keyword 'End'.

We don't attempt full semantic parsing — that would need the entire FDMNES
keyword catalog. Instead we group lines by leading keyword and let the
caller interpret the contents.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


# 9-char truncation matches the FDMNES parser behaviour
_KW_TRUNC = 9


def _is_keyword_line(line: str) -> bool:
    """A keyword line starts with an alphabetic token that is not path-like."""
    s = line.strip()
    if not s or s.startswith("!"):
        return False
    first = s.split()[0]
    # Path-like / filename-like tokens are values, not keywords.
    # FDMNES keywords never contain '/', '.', '\\', or '~'.
    if any(c in first for c in "/.\\~"):
        return False
    try:
        float(first)
        return False
    except ValueError:
        pass
    return first[0].isalpha()


def parse_input(path_or_content: str | Path) -> dict[str, Any]:
    """
    Parse an FDMNES input file or string.

    Returns:
      - source: 'path' if given a Path that exists, else 'inline'
      - blocks: list of {'keyword': str, 'keyword_canonical': str (9-char),
                          'values': list[str], 'lineno': int}
      - keywords: dict[keyword -> list[block]] (case-insensitive)
      - has_end: bool
      - n_blocks: int
    """
    p = None
    if isinstance(path_or_content, Path) or (
        isinstance(path_or_content, str) and "\n" not in path_or_content
        and Path(path_or_content).exists()
    ):
        p = Path(path_or_content)
        text = p.read_text(errors="replace")
        source = "path"
    else:
        text = str(path_or_content)
        source = "inline"

    lines = text.splitlines()

    blocks: list[dict] = []
    current: dict | None = None
    has_end = False

    for i, raw in enumerate(lines, start=1):
        s = raw.strip()
        if not s or s.startswith("!"):
            continue
        if _is_keyword_line(raw):
            kw = s.split()[0]
            kw_l = kw.lower()
            if kw_l in ("end", "fin", "fine"):
                has_end = True
                if current is not None:
                    blocks.append(current)
                    current = None
                break
            # Close previous block
            if current is not None:
                blocks.append(current)
            current = {
                "keyword": kw,
                "keyword_canonical": kw_l[:_KW_TRUNC],
                "values": [],
                "lineno": i,
            }
            # Any remaining tokens on the same line are part of the value
            rest = s.split(None, 1)
            if len(rest) > 1:
                current["values"].append(rest[1])
        else:
            if current is None:
                # Value before any keyword — orphan, skip
                continue
            current["values"].append(s)

    if current is not None and not has_end:
        blocks.append(current)

    keywords: dict[str, list[dict]] = {}
    for b in blocks:
        keywords.setdefault(b["keyword"].lower(), []).append(b)

    out = {
        "source": source,
        "n_blocks": len(blocks),
        "has_end": has_end,
        "blocks": blocks,
        "keywords": keywords,
    }
    if p:
        out["path"] = str(p)
    return out
