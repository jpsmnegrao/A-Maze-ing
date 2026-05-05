"""Tests for generated maze validity (borders, path, 42 pattern).

Tests run against multiple seeds so coverage isn't tied to a single maze.
"""


import pytest
from typing import Any, Dict, List, Tuple
from algorithm.wilson_generator import Maze


def make_maze(tmp_path: Any, seed: int) -> Tuple[
        List[List[int]], Tuple[int, int], Tuple[int, int], str]:
    """Run the generator and return parsed grid, entry, exit, path."""
    cfg: Dict[str, Any] = {
        "WIDTH": 9, "HEIGHT": 7,
        "ENTRY": (1, 0), "EXIT": (4, 4),
        "OUTPUT_FILE": str(tmp_path / "maze.txt"),
        "PERFECT": True, "SEED": seed,
    }
    maze = Maze(cfg)
    maze.sleep_timer = 0
    maze.generate_maze(cfg["OUTPUT_FILE"])
    with open(cfg["OUTPUT_FILE"]) as f:
        lines = [line.rstrip("\n") for line in f]
    blank = lines.index("")
    grid: List[List[int]] = [
        [int(ch, 16) for ch in row] for row in lines[:blank]
    ]
    parts_e = lines[blank + 1].split(",")
    entry: Tuple[int, int] = (int(parts_e[0]), int(parts_e[1]))
    parts_x = lines[blank + 2].split(",")
    exit_: Tuple[int, int] = (int(parts_x[0]), int(parts_x[1]))
    path = lines[blank + 3]
    return grid, entry, exit_, path


SEEDS = [42, 100, 7, 999, 12345]


@pytest.mark.parametrize("seed", SEEDS)
def test_borders_closed(tmp_path: Any, seed: int) -> None:
    grid, _, _, _ = make_maze(tmp_path, seed)
    h, w = len(grid), len(grid[0])
    for x in range(w):
        assert grid[0][x] & 1, f"top border open at ({x},0)"
        assert grid[h-1][x] & 4, f"bottom border open at ({x},{h-1})"
    for y in range(h):
        assert grid[y][0] & 8, f"left border open at (0,{y})"
        assert grid[y][w-1] & 2, f"right border open at ({w-1},{y})"


@pytest.mark.parametrize("seed", SEEDS)
def test_path_in_bounds(tmp_path: Any, seed: int) -> None:
    grid, entry, _, path = make_maze(tmp_path, seed)
    h, w = len(grid), len(grid[0])
    x, y = entry
    for letter in path:
        if letter == "N":
            y -= 1
        elif letter == "S":
            y += 1
        elif letter == "E":
            x += 1
        elif letter == "W":
            x -= 1
        assert 0 <= x < w and 0 <= y < h, \
            f"path went out of bounds to ({x},{y})"


@pytest.mark.parametrize("seed", SEEDS)
def test_path_reaches_exit(tmp_path: Any, seed: int) -> None:
    _, entry, exit_, path = make_maze(tmp_path, seed)
    x, y = entry
    for letter in path:
        if letter == "N":
            y -= 1
        elif letter == "S":
            y += 1
        elif letter == "E":
            x += 1
        elif letter == "W":
            x -= 1
    assert (x, y) == exit_, f"path ended at ({x},{y}), expected {exit_}"


@pytest.mark.parametrize("seed", SEEDS)
def test_path_doesnt_cross_walls(tmp_path: Any, seed: int) -> None:
    grid, entry, _, path = make_maze(tmp_path, seed)
    x, y = entry
    for i, letter in enumerate(path):
        cell = grid[y][x]
        if letter == "N":
            assert not (cell & 1), f"step {i}: N wall closed at ({x},{y})"
            y -= 1
        elif letter == "S":
            assert not (cell & 4), f"step {i}: S wall closed at ({x},{y})"
            y += 1
        elif letter == "E":
            assert not (cell & 2), f"step {i}: E wall closed at ({x},{y})"
            x += 1
        elif letter == "W":
            assert not (cell & 8), f"step {i}: W wall closed at ({x},{y})"
            x -= 1


@pytest.mark.parametrize("seed", SEEDS)
def test_42_pattern_cells_closed(tmp_path: Any, seed: int) -> None:
    grid, _, _, _ = make_maze(tmp_path, seed)
    h, w = len(grid), len(grid[0])
    pattern = [
        [1, 0, 0, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1],
    ]
    pcol = (w // 2) - 3
    prow = (h // 2) - 2
    for r in range(5):
        for c in range(7):
            if pattern[r][c] == 1:
                assert grid[prow + r][pcol + c] == 0xF, \
                    f"42 cell ({pcol+c},{prow+r}) not fully closed"
