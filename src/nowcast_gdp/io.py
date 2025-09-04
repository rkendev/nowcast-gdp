from pathlib import Path
from typing import Iterable


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def _read_nonempty_lines(path: Path) -> list[str]:
    """
    Read path as plain text lines (no header), stripping empties.
    Returns [] if the file does not exist.
    """
    if not path.exists():
        return []
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _write_lines(path: Path, lines: list[str]) -> None:
    """
    Write plain text lines with a trailing newline when non-empty.
    """
    ensure_dir(path.parent)
    if lines:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        # create/empty the file explicitly
        path.write_text("", encoding="utf-8")


def write_index_unique_sorted(path: Path, values: Iterable[str]) -> None:
    """
    Maintain a newline-delimited index file (no header) of vintage dates.
    Behavior:
      - creates the file if missing
      - merges with any existing lines
      - removes duplicates
      - sorts ascending (lexicographic works for YYYY-MM-DD)
    """
    existing = set(_read_nonempty_lines(path))
    incoming = {v for v in values if v}
    merged = sorted(existing | incoming)
    _write_lines(path, merged)
