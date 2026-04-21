"""
Version 2.1
Module: a-maze-ing
Main entrypoint for a-maze-ing maze generator and solver.
"""

from config import ParserReturn
from mlx_renderer import MazeRenderer


parser = ParserReturn("config.txt")
config = parser.parse_config()

renderer = MazeRenderer(config)
renderer.run_mlx_renderer()
renderer.draw_maze()
