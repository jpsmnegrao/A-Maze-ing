"""
Main entrypoint for a-maze-ing maze generator and solver.

Uses ParserReturn for config parsing, Maze for generation,
and MazeRenderer for visual display.

Version 2.1
"""

import sys
from typing import List, Dict, Any
from config import ParserReturn
from mlx_renderer import MazeRenderer
from algorithm.wilson_generator import Maze


if len(sys.argv) != 2:
    print("Usage: python3 a_maze_ing.py config.txt")
    sys.exit(1)
parser: ParserReturn = ParserReturn(sys.argv[1])
config: Dict[str, Any] = parser.parse_config()
maze_gen: Maze = Maze(config)

maze_gen.sleep_timer = 0

maze_gen.generate_maze(config["OUTPUT_FILE"])
maze_grid: List[List[int]] = []
with open(config["OUTPUT_FILE"], "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            break
        maze_grid.append([int(ch, 16) for ch in line])
    # skip entry and exit points
    f.readline()
    f.readline()
    path_line = f.readline().strip()
renderer: MazeRenderer = MazeRenderer(config)
renderer.path = list(path_line)
renderer.animation_frames = [
    (col, row, maze_grid[row][col])
    for row in range(len(maze_grid))
    for col in range(len(maze_grid[row]))
]
renderer.run_mlx_renderer(maze_grid)
