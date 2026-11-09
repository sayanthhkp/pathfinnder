"""CSV map loading and validation."""
import csv

ALLOWED = {".", "#", "~"}

class MapFormatError(ValueError):
    pass

def load_map(path):
    try:
        with open(path, "r", newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.reader(handle))
    except OSError as exc:
        raise MapFormatError(f"Cannot read map file: {exc}") from exc

    if not rows:
        raise MapFormatError("Map file is empty.")
    if any(not row for row in rows):
        raise MapFormatError("Map contains an empty row.")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise MapFormatError("Map must be rectangular: every row needs the same number of cells.")
    if len(rows) < 20 or width < 20:
        raise MapFormatError("Map must be at least 20 rows by 20 columns.")

    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            if value not in ALLOWED:
                raise MapFormatError(
                    f"Invalid cell {value!r} at row {r+1}, column {c+1}. "
                    "Use . for walkway, # for wall, and ~ for slow ground."
                )
    return rows
