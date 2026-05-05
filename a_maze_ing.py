"""Main entrypoint for a-maze-ing maze generator and solver.

Uses ParserReturn for config parsing, Maze for generation, and MazeRenderer
for visual display.

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
try:
    parser: ParserReturn = ParserReturn(sys.argv[1])
    config: Dict[str, Any] = parser.parse_config()
except ValueError as error:
    print(f"Error: {error}")
    sys.exit(1)
# Instantiate the generator and disable its per-step animation delay
maze_gen: Maze = Maze(config)
maze_gen.sleep_timer = 0
# Generate the maze and write it to the configured output file
maze_gen.generate_maze(config["OUTPUT_FILE"])
# Read the generated maze back from the output file
maze_grid: List[List[int]] = []
with open(config["OUTPUT_FILE"], "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            break
        maze_grid.append([int(ch, 16) for ch in line])
    # Skip entry and exit points
    f.readline()
    f.readline()
    path_line = f.readline().strip()
# Wire up the renderer with the maze data, path, and per-cell animation frames
renderer: MazeRenderer = MazeRenderer(config, maze_gen)
renderer.path = list(path_line)
renderer.animation_frames = [
    (col, row, maze_grid[row][col])
    for row in range(len(maze_grid))
    for col in range(len(maze_grid[row]))
]
# Open the MLX window and start the event loop
renderer.run_mlx_renderer(maze_grid)
