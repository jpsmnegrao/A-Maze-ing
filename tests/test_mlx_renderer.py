"""
Module: test_mlx_renderer
Pytest script to test config parsing.
"""


from typing import Any, Dict
from mlx_renderer import MazeRenderer
from algorithm.wilson_generator import Maze


def make_config(width: int = 9, height: int = 7) -> Dict[str, Any]:
    """Build a minimal config dict for instantiating MazeRenderer."""
    return {
        "WIDTH": width,
        "HEIGHT": height,
        "ENTRY": (1, 0),
        "EXIT": (4, 4),
        "OUTPUT_FILE": "maze.txt",
        "PERFECT": True,
    }


def make_renderer(width: int = 9, height: int = 7) -> MazeRenderer:
    """Build a MazeRenderer with a real Maze instance for testing."""
    cfg = make_config(width, height)
    return MazeRenderer(cfg, Maze(cfg))

# ---------- reset_maze ----------


def test_reset_maze_cell_size_fits_in_area() -> None:
    """cell_size must fit width*cell and height*cell inside the maze area."""
    r = make_renderer(9, 7)
    r.reset_maze()
    assert r.cell_size > 0
    assert r.cell_size * r.maze_width <= r.maze_area_width
    assert r.cell_size * r.maze_height <= r.maze_area_height


def test_reset_maze_wall_thickness_minimum() -> None:
    """wall_thickness must be at least 1, even for tiny cells."""
    r = make_renderer(50, 50)
    r.reset_maze()
    assert r.wall_thickness >= 1
    assert r.wall_thickness <= 5


def test_reset_maze_initialises_grid_with_closed_cells() -> None:
    """After reset, self.maze must be height x width filled with 15 (all walls
    closed)."""
    r = make_renderer(9, 7)
    r.reset_maze()
    assert len(r.maze) == 7
    assert all(len(row) == 9 for row in r.maze)
    assert all(cell == 15 for row in r.maze for cell in row)


def test_reset_maze_start_position_non_negative() -> None:
    """start_x and start_y must be non-negative for any reasonable maze
    size."""
    for w, h in [(5, 5), (9, 7), (20, 15), (30, 30)]:
        r = make_renderer(w, h)
        r.reset_maze()
        assert r.start_x >= 0, f"start_x negative for {w}x{h}"
        assert r.start_y >= 0, f"start_y negative for {w}x{h}"


# ---------- rotate_themes ----------

def test_rotate_themes_cycles_through_all() -> None:
    """rotate_themes must cycle through all themes and return to the first."""
    r = make_renderer()
    initial_theme = r.theme_name
    r.rotate_themes()
    assert r.theme_name != initial_theme
    r.rotate_themes()
    r.rotate_themes()
    assert r.theme_name == initial_theme


def test_rotate_themes_updates_colors() -> None:
    """Rotating must change the color attributes."""
    r = make_renderer()
    initial_wall = r.color_wall
    initial_path = r.color_path
    r.rotate_themes()
    # At least one color should change
    assert (r.color_wall != initial_wall) or (r.color_path != initial_path)


def test_rotate_themes_index_in_range() -> None:
    """current_theme index must always stay within bounds."""
    r = make_renderer()
    for _ in range(10):
        r.rotate_themes()
        assert 0 <= r.current_theme < 3


# ---------- constructor / config wiring ----------

def test_constructor_stores_config_values() -> None:
    """Constructor must store WIDTH/HEIGHT/ENTRY/EXIT from config."""
    cfg = make_config(20, 15)
    cfg["ENTRY"] = (3, 4)
    cfg["EXIT"] = (10, 10)
    r = MazeRenderer(cfg, Maze(cfg))
    assert r.maze_width == 20
    assert r.maze_height == 15
    assert r.entry == (3, 4)
    assert r.exit == (10, 10)
