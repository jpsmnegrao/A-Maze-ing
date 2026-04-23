"""
Version 2.1
Module: mlx_renderer
mambo.
"""


from typing import Dict, List, Tuple, Optional, Any
from mlx import Mlx  # type: ignore


# TODO: replace with import when generator module is ready
# from mazegen import N, S, E, W
N, S, E, W = 1, 2, 4, 8


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
        self.maze_area_width = 610
        self.maze_area_height = 610
        self.cell_size = 0
        self.wall_thickness = max(1, self.cell_size // 10)
        self.show_path: bool = False
        self.maze: List[List[int]] = []
        self.path: List[List[int]] = []
        # MLX objects (initialized in run_renderer)
        self.mlx: Optional[Mlx] = None
        self.mlx_ptr: Optional[Any] = None
        self.win_ptr: Optional[Any] = None
        self.image: Optional[Any] = None
        self.data: Optional[Any] = None
        self.bpp: Optional[Any] = None
        self.size_line: Optional[int] = None
        self.iformat: Optional[Any] = None
        self.bg_image: Optional[Any] = None
        self.bg_data: Optional[Any] = None
        self.bg_size_line: Optional[int] = None
        # Theme objects
        self.theme_name: str = "Dark"
        self.current_theme: int = 0
        self.color_window_bg: int = 0xFF000000
        self.color_maze_area: int = 0xFF666666
        self.color_wall: int = 0xFF000000
        self.color_pattern: int = 0xFF333333
        self.color_text: int = 0xFF333333

    def run_mlx_renderer(self, maze: List[List[int]]) -> None:
        """mambo"""
        self.maze = maze
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(
                       self.mlx_ptr, self.window_height, self.window_width,
                       "A-Maze-ing"
                )
        self.bg_image = self.mlx.mlx_new_image(
            self.mlx_ptr, self.window_height, self.window_width)
        self.bg_data, _, self.bg_size_line, _ = (
            self.mlx.mlx_get_data_addr(self.bg_image))
        self.image = self.mlx.mlx_new_image(
                     self.mlx_ptr, self.window_height, self.window_width)
        self.data, self.bpp, self.size_line, self.iformat = (
            self.mlx.mlx_get_data_addr(self.image))
        self.draw_canvas(maze)
        self.mlx.mlx_mouse_hook(self.win_ptr, self.mouse_handler, None)
        self.mlx.mlx_key_hook(self.win_ptr, self.key_handler, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.close_handle, None)
        self.mlx.mlx_loop(self.mlx_ptr)

    def draw_canvas(self, maze: List[List[int]]) -> None:
        """jambo"""
        if self.mlx is None:
            return
        if self.bg_size_line is not None \
                and self.bg_data is not None:
            for y in range(self.window_height):
                for x in range(self.window_width):
                    offset: int = (y * self.bg_size_line) + (x * 4)
                    self.bg_data[offset:offset+4] = (
                        self.color_window_bg.to_bytes(4, 'little'))
        if self.size_line is not None \
                and self.data is not None:
            for y in range(self.maze_area_height + 10):
                for x in range(self.maze_area_width + 10):
                    offset = (y * self.size_line) + (x * 4)
                    self.data[offset:offset+4] = (
                        (self.color_maze_area).to_bytes(4, 'little')
                    )
        self.draw_maze(maze)

        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                         self.bg_image, 0, 0)
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                         self.image, 95, 45)
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 309, 15,
                                self.color_text, "=== A-Maze-ing ===")
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 678,
                                self.color_text, '1. Regenerate maze')
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 700,
                                self.color_text, '2. Show/hide path from entry'
                                                 'to exit')
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 722,
                                self.color_text, '3. Rotate themes (current '
                                f'{self.theme_name})')
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 744,
                                self.color_text, '4. Exit')
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 766,
                                self.color_text, 'Choose one: ')

    def draw_maze(self, maze: List[List[int]]) -> None:
        """jambo"""
        # Calculate cell size as the largest size that fits the maze
        self.cell_size = min(
            (self.maze_area_width - self.wall_thickness * 2) // len(maze[0]),
            (self.maze_area_height - self.wall_thickness * 2) // len(maze)
        )
        self.wall_thickness = max(1, min(self.cell_size // 10, 5))
        # Calculate maze pixel dimensions and centered starting position
        # within the grey area
        maze_pixel_width: int = len(maze[0]) * self.cell_size
        maze_pixel_height: int = len(maze) * self.cell_size
        start_x: int = max(
            self.wall_thickness, (self.maze_area_width - maze_pixel_width) // 2
        )
        start_y: int = max(
            self.wall_thickness,
            (self.maze_area_height - maze_pixel_height) // 2
        )
        if self.maze_width >= 13 or self.maze_height >= 13:
            start_x += 3
            start_y += 3
        # Draw 42 pattern if maze is large enough and store its grid position
        pattern_42: List[List[int]] = [
            [1, 0, 1, 0, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 1, 1],
            [1, 1, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
        pattern_col: int = -1
        pattern_row: int = -1
        if self.maze_width > 8 or self.maze_height > 10:
            pattern_col, pattern_row = self.draw_42_pattern(
                start_x, start_y, len(maze[0]), len(maze), pattern_42)
        for row in range(len(maze)):
            for col in range(len(maze[row])):
                cell_x: int = start_x + (col * self.cell_size)
                cell_y: int = start_y + (row * self.cell_size)
                cell: int = maze[row][col]
                # Check if current cell is part of the 42 pattern
                p_row: int = row - pattern_row
                p_col: int = col - pattern_col
                is_pattern_cell = (
                    pattern_col >= 0 and
                    0 <= p_row < len(pattern_42) and
                    0 <= p_col < len(pattern_42[0]) and
                    pattern_42[p_row][p_col] == 1
                )
                # Check if each neighbouring cell is part of the 42 pattern
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
                # Force walls closed for pattern cells and their neighbours
                north: bool = True if (is_pattern_cell or north_is_pattern) \
                    else bool(cell & N)
                south: bool = True if (is_pattern_cell or south_is_pattern) \
                    else bool(cell & S)
                west: bool = True if (is_pattern_cell or west_is_pattern) \
                    else bool(cell & W)
                east: bool = True if (is_pattern_cell or east_is_pattern) \
                    else bool(cell & E)
                # Draw walls for current cell
                if north:
                    for wall_row in range(self.wall_thickness):
                        for x in range(cell_x, cell_x + self.cell_size):
                            if self.size_line is not None \
                                    and self.data is not None:
                                offset: int = (
                                        ((cell_y + wall_row)
                                         * self.size_line) + (x * 4)
                                    )
                                self.data[offset:offset+4] = (
                                    (self.color_wall).to_bytes(4, 'little'))
                if south:
                    for wall_row in range(self.wall_thickness):
                        for x in range(
                                cell_x,
                                cell_x + self.cell_size + self.wall_thickness):
                            if self.size_line is not None \
                                    and self.data is not None:
                                offset = (
                                        (((cell_y + self.cell_size) + wall_row)
                                         * self.size_line) + (x * 4)
                                    )
                                self.data[offset:offset+4] = (
                                    (self.color_wall).to_bytes(4, 'little'))
                if west:
                    for wall_col in range(self.wall_thickness):
                        for y in range(cell_y, cell_y + self.cell_size):
                            if self.size_line is not None \
                                    and self.data is not None:
                                offset = (
                                    (y * self.size_line) +
                                    ((cell_x + wall_col) * 4)
                                )
                                self.data[offset:offset+4] = (
                                    (self.color_wall).to_bytes(4, 'little'))
                if east:
                    for wall_col in range(self.wall_thickness):
                        for y in range(
                                cell_y,
                                cell_y + self.cell_size + self.wall_thickness):
                            if self.size_line is not None \
                                    and self.data is not None:
                                offset = (
                                    (y * self.size_line) +
                                    ((cell_x + self.cell_size + wall_col) * 4)
                                )
                                self.data[offset:offset+4] = (
                                    (self.color_wall).to_bytes(4, 'little'))

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
                            if self.size_line is not None \
                                    and self.data is not None:
                                if not (
                                        pixel_x < 0
                                        or pixel_y < 0
                                        or pixel_x > self.maze_area_width
                                        or pixel_y > self.maze_area_height
                                        ):

                                    offset = (
                                        pixel_y * self.size_line) + (pixel_x
                                                                     * 4)
                                    self.data[offset:offset+4] = (
                                        (self.color_pattern).to_bytes(4,
                                                                      'little')
                                    )
        return pattern_col, pattern_row

    def rotate_themes(self) -> None:
        """jambo"""
        themes = [
            {
                "theme_name": "Dark",
                "color_window_bg": 0xFF000000,
                "color_maze_area": 0xFF666666,
                "color_wall": 0xFF000000,
                "color_pattern": 0xFF333333,
                "color_text": 0xFF333333,
            },
            {
                "theme_name": "Negative",
                "color_window_bg": 0xFFD0D0D0,
                "color_maze_area": 0xFFB0B0B0,
                "color_wall": 0xFF404040,
                "color_pattern": 0xFF888888,
                "color_text": 0xFF303030,
            },
            {
                "theme_name": "42",
                "color_window_bg": 0xFF1A0A00,
                "color_maze_area": 0xFF2B6CB0,
                "color_wall": 0xFF5C3317,
                "color_pattern": 0xFF1A5276,
                "color_text": 0xFF5C3317,
            },
        ]
        self.current_theme = (self.current_theme + 1) % len(themes)
        for key, value in themes[self.current_theme].items():
            if key != "name":
                setattr(self, key, value)

    def mouse_handler(self, button, x, y, mystuff):
        print(f"Got mouse event! button {button} at {x},{y}.")

    def key_handler(self, keynum, mystuff):
        print(mystuff)
        if keynum == 32:
            self.mlx.mlx_mouse_hook(self.win_ptr, None, None)
        if keynum in (52, 65430):
            self.mlx.mlx_loop_exit(self.mlx_ptr)
            print("You pressed to exit - bye!")
        elif keynum in (51, 65435):
            self.rotate_themes()
            self.draw_canvas(self.maze)
        else:
            print(f"Got key {keynum}, and got my stuff back:")

    def close_handle(self, dummy):
        self.mlx.mlx_loop_exit(self.mlx_ptr)
