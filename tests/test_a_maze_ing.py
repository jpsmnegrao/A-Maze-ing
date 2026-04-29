"""Integration tests for the maze generator output file format.

These tests call the generator classes directly (no subprocess, no renderer).
They validate that the output file conforms to the spec, regardless of the
actual maze contents.
"""

import re
from pathlib import Path
from typing import Any, Dict

from algorithm.wilson_generator import Maze


def make_config(tmp_path: Path, **overrides: Any) -> Dict[str, Any]:
    """Build a config dict matching what ParserReturn would produce."""
    config: Dict[str, Any] = {
        "WIDTH": 9,
        "HEIGHT": 7,
        "ENTRY": (1, 0),
        "EXIT": (4, 4),
        "OUTPUT_FILE": str(tmp_path / "maze.txt"),
        "PERFECT": True,
        "SEED": 42,
    }
    config.update(overrides)
    return config


def generate(tmp_path: Path, **overrides: Any) -> Path:
    """Run the generator with given overrides and return the output path."""
    config = make_config(tmp_path, **overrides)
    maze = Maze(config)
    maze.sleep_timer = 0
    maze.generate_maze(config["OUTPUT_FILE"])
    return Path(config["OUTPUT_FILE"])


# ---------- Output file format ----------

def test_output_file_is_created(tmp_path: Path) -> None:
    """Generator must produce the file specified in OUTPUT_FILE."""
    out = generate(tmp_path)
    assert out.exists(), f"Generator did not create {out}"


def test_grid_dimensions_match_config(tmp_path: Path) -> None:
    """Output grid must have HEIGHT rows of WIDTH hex chars each."""
    out = generate(tmp_path, WIDTH=9, HEIGHT=7)
    with open(out) as f:
        lines = f.readlines()
    grid_lines = []
    for line in lines:
        stripped = line.rstrip("\n")
        if stripped == "":
            break
        grid_lines.append(stripped)
    assert len(grid_lines) == 7, f"Expected 7 rows, got {len(grid_lines)}"
    for i, row in enumerate(grid_lines):
        assert len(row) == 9, f"Row {i} has {len(row)} chars, expected 9"


def test_grid_contains_only_hex_digits(tmp_path: Path) -> None:
    """Every cell must be a single hex digit 0-F."""
    out = generate(tmp_path)
    with open(out) as f:
        for line in f:
            stripped = line.rstrip("\n")
            if stripped == "":
                break
            assert re.fullmatch(r"[0-9A-Fa-f]+", stripped), \
                f"Non-hex chars in grid line: {stripped!r}"


def test_blank_separator_after_grid(tmp_path: Path) -> None:
    """Grid must be followed by an empty line per spec."""
    out = generate(tmp_path)
    with open(out) as f:
        lines = f.readlines()
    blank_idx = next(
        (i for i, line in enumerate(lines) if line.rstrip("\n") == ""),
        -1,
    )
    assert blank_idx > 0, "No blank separator line found after grid"


def test_entry_exit_path_lines_present(tmp_path: Path) -> None:
    """The 3 lines after the blank must be entry, exit, path."""
    out = generate(tmp_path, ENTRY=(1, 0), EXIT=(4, 4))
    with open(out) as f:
        lines = [line.rstrip("\n") for line in f]
    blank_idx = lines.index("")
    assert len(lines) > blank_idx + 3, \
        "File too short: missing entry/exit/path lines"
    entry_line = lines[blank_idx + 1]
    exit_line = lines[blank_idx + 2]
    path_line = lines[blank_idx + 3]
    assert re.fullmatch(r"\d+,\d+", entry_line), \
        f"Entry line malformed: {entry_line!r}"
    assert re.fullmatch(r"\d+,\d+", exit_line), \
        f"Exit line malformed: {exit_line!r}"
    assert re.fullmatch(r"[NESW]*", path_line), \
        f"Path contains non-NESW chars: {path_line!r}"


def test_entry_coordinates_match_config(tmp_path: Path) -> None:
    """Entry line in file must equal ENTRY from config."""
    out = generate(tmp_path, ENTRY=(1, 0))
    with open(out) as f:
        lines = [line.rstrip("\n") for line in f]
    blank_idx = lines.index("")
    assert lines[blank_idx + 1] == "1,0"


def test_exit_coordinates_match_config(tmp_path: Path) -> None:
    """Exit line in file must equal EXIT from config (catches the x,x bug)."""
    out = generate(tmp_path, EXIT=(4, 4))
    with open(out) as f:
        lines = [line.rstrip("\n") for line in f]
    blank_idx = lines.index("")
    assert lines[blank_idx + 2] == "4,4"


def test_all_lines_end_with_newline(tmp_path: Path) -> None:
    """Spec: all lines must end with \\n, including the last one."""
    out = generate(tmp_path)
    with open(out, "rb") as f:
        content = f.read()
    assert content.endswith(b"\n"), \
        "Last line of output file does not end with newline"


# ---------- Reproducibility ----------

def test_same_seed_produces_same_output(tmp_path: Path) -> None:
    """Running with the same SEED twice must produce identical output."""
    a_dir = tmp_path / "a"
    b_dir = tmp_path / "b"
    a_dir.mkdir()
    b_dir.mkdir()
    out1 = generate(a_dir, SEED=123)
    content1 = out1.read_text()
    out2 = generate(b_dir, SEED=123)
    content2 = out2.read_text()
    assert content1 == content2, \
        "Same SEED produced different output (reproducibility broken)"
