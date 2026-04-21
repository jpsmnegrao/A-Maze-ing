"""
Version 2.1
Module: mlx_renderer
mambo.
"""


from typing import Dict, List, Tuple, Any
from mlx import Mlx  # type: ignore


class MazeRenderer:
    """mambo"""

    def __init__(self, config: Dict[str, Any]) -> None:
        """jambo"""
        self.config = config
        self.window_width = 800
        self.window_height = 800
        self.maze_width = config["WIDTH"]
        self.maze_height = config["HEIGHT"]
        self.entry = config["ENTRY"]
        self.exit = config["EXIT"]
        self.output_file = config["OUTPUT_FILE"]
        self.perfect = config["PERFECT"]
        self.maze_area_width = 600
        self.maze_area_height = 600
        self.cell_size = 0
        self.wall_thickness = max(1, self.cell_size // 10)
        self.show_path: bool = False
        self.wall_color: int = 0xFFFFFFF
        # MLX objects (initialized in run_renderer)
        self.mlx = None
        self.mlx_ptr = None
        self.win_ptr = None
        self.image = None
        self.data = None
        self.bpp = None
        self.size_line: int | None = None
        self.iformat = None

    def run_mlx_renderer(self, maze: List[List[Dict[str, bool]]]) -> None:
        """mambo"""
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(self.mlx_ptr, 
                       self.window_height, self.window_width, "A-Maze-ing")
        self.image = self.mlx.mlx_new_image(self.mlx_ptr,
                     self.window_height, self.window_width)
        self.data, self.bpp, self.size_line, self.iformat = (
            self.mlx.mlx_get_data_addr(self.image))
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 309, 15,
                                0xFF333333, "=== A-Maze-ing ===")
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 665,
                                0xFF333333, '1. Regenerate maze')
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 690,
                                0xFF333333, '2. Show/hide path from entry to '
                                            'exit')
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 715,
                                0xFF333333, '3. Rotate maze colors')
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 740,
                                0xFF333333, '4. Exit')
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 765,
                                0xFF333333, 'Choose one: ')
        for y in range(self.maze_area_height + 10):
            for x in range(self.maze_area_width + 10):
                offset = (y * self.size_line) + (x * 4)
                self.data[offset:offset+4] = (0xFF666666).to_bytes(4, 'little')
        self.draw_maze(maze)
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                         self.image, 95, 45)
        self.mlx.mlx_mouse_hook(self.win_ptr, self.mouse_handler, None)
        self.mlx.mlx_key_hook(self.win_ptr, self.key_handler, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.close_handle, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def draw_maze(self, maze: List[List[Dict[str, bool]]]) -> None:
        """jambo"""
        self.cell_size = min(
            self.maze_area_width // len(maze[0]),
            self.maze_area_height // len(maze)
        )
        self.wall_thickness = max(1, self.cell_size // 10)
        maze_pixel_width = len(maze[0]) * self.cell_size
        maze_pixel_height = len(maze) * self.cell_size
        start_x = (self.maze_area_width - maze_pixel_width) // 2
        start_y = (self.maze_area_height - maze_pixel_height) // 2
        pattern_42 = [
            [1, 0, 1, 0, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 1],
            [1, 1, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
        pattern_col, pattern_row = -1, -1
        if self.maze_width > 8 or self.maze_height > 10:
            pattern_col, pattern_row = self.draw_42_pattern(
                start_x, start_y, len(maze[0]), len(maze), pattern_42)
        for row in range(len(maze)):
            for col in range(len(maze[row])):
                cell_x = start_x + (col * self.cell_size)
                cell_y = start_y + (row * self.cell_size)
                cell: Dict[str, bool] = maze[row][col]
                p_row = row - pattern_row
                p_col = col - pattern_col
                is_pattern_cell = (
                    pattern_col >= 0 and
                    0 <= p_row < len(pattern_42) and
                    0 <= p_col < len(pattern_42[0]) and
                    pattern_42[p_row][p_col] == 1
                )
                north_is_pattern = (
                    pattern_col >= 0 and
                    0 <= (row - 1) - pattern_row < len(pattern_42) and
                    0 <= col - pattern_col < len(pattern_42[0]) and
                    pattern_42[(row - 1) - pattern_row][col - pattern_col] == 1
                )
                south_is_pattern = (
                    pattern_col >= 0 and
                    0 <= (row + 1) - pattern_row < len(pattern_42) and
                    0 <= col - pattern_col < len(pattern_42[0]) and
                    pattern_42[(row + 1) - pattern_row][col - pattern_col] == 1
                )
                east_is_pattern = (
                    pattern_col >= 0 and
                    0 <= row - pattern_row < len(pattern_42) and
                    0 <= (col + 1) - pattern_col < len(pattern_42[0]) and
                    pattern_42[row - pattern_row][(col + 1) - pattern_col] == 1
                )
                west_is_pattern = (
                    pattern_col >= 0 and
                    0 <= row - pattern_row < len(pattern_42) and
                    0 <= (col - 1) - pattern_col < len(pattern_42[0]) and
                    pattern_42[row - pattern_row][(col - 1) - pattern_col] == 1
                )
                north = True if (is_pattern_cell or north_is_pattern) \
                    else cell["north"]
                south = True if (is_pattern_cell or south_is_pattern) \
                    else cell["south"]
                west = True if (is_pattern_cell or west_is_pattern) \
                    else cell["west"]
                east = True if (is_pattern_cell or east_is_pattern) \
                    else cell["east"]
                if north:
                    for wall_row in range(self.wall_thickness):
                        for x in range(cell_x, cell_x + self.cell_size):
                            if self.size_line is not None:
                                offset = (
                                    (((cell_y + self.cell_size) + wall_row) *
                                     self.size_line) + (x * 4)
                                )
                                self.data[offset:offset+4] = (
                                    (0xFF000000).to_bytes(4, 'little'))
                if south:
                    for wall_row in range(self.wall_thickness):
                        for x in range(cell_x, cell_x + self.cell_size):
                            if self.size_line is not None:
                                offset = (
                                    (((cell_y + self.cell_size) + wall_row) *
                                     self.size_line) + (x * 4)
                                )
                                self.data[offset:offset+4] = (
                                    (0xFF000000).to_bytes(4, 'little'))
                if west:
                    for wall_col in range(self.wall_thickness):
                        for y in range(cell_y, cell_y + self.cell_size):
                            if self.size_line is not None:
                                offset = (
                                    (y * self.size_line) +
                                    ((cell_x + wall_col) * 4)
                                )
                                self.data[offset:offset+4] = (
                                    (0xFF000000).to_bytes(4, 'little'))
                if east:
                    for wall_col in range(self.wall_thickness):
                        for y in range(cell_y, cell_y + self.cell_size):
                            if self.size_line is not None:
                                offset = (
                                    (y * self.size_line) +
                                    ((cell_x + self.cell_size + wall_col) * 4)
                                )
                                self.data[offset:offset+4] = (
                                    (0xFF000000).to_bytes(4, 'little'))

    def draw_42_pattern(self, start_x: int, start_y: int,
                        len_maze_cols: int, len_maze_rows: int,
                        pattern_42: List[List[int]]) -> Tuple[int, int]:
        """Draw the '42' pattern using fully closed cells."""
        pattern_42 = [
            [1, 0, 1, 0, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 1],
            [1, 1, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
        pattern_col = (len_maze_cols - len(pattern_42[0])) // 2
        pattern_row = (len_maze_rows - len(pattern_42)) // 2
        pattern_start_x = start_x + (pattern_col * self.cell_size)
        pattern_start_y = start_y + (pattern_row * self.cell_size)
        for row in range(len(pattern_42)):
            for col in range(len(pattern_42[row])):
                if pattern_42[row][col] == 1:
                    cell_x = pattern_start_x + (col * self.cell_size)
                    cell_y = pattern_start_y + (row * self.cell_size)
                    for py in range(self.cell_size):
                        for px in range(self.cell_size):
                            pixel_x = cell_x + px
                            pixel_y = cell_y + py
                            offset = (pixel_y * self.size_line) + (pixel_x * 4)
                            self.data[offset:offset+4] = (0xFF888888).to_bytes(
                                4, 'little')
        return pattern_col, pattern_row

    def mouse_handler(self, button, x, y, mystuff):
        print(f"Got mouse event! button {button} at {x},{y}.")

    def key_handler(self, keynum, mystuff):
        print(f"Got key {keynum}, and got my stuff back:")
        print(mystuff)
        if keynum == 32:
            self.mlx.mlx_mouse_hook(self.win_ptr, None, None)

    def close_handle(self, dummy):
        self.mlx.mlx_loop_exit(self.mlx_ptr)
