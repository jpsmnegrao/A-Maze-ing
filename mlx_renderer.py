"""
Version 2.1
Module: mlx_renderer
mambo.
"""


from typing import Dict, List, Tuple, Optional, Any
from mlx import Mlx  # type: ignore


# TODO: replace with import when generator module is ready
# from mazegen import N, S, E, W
N, E, S, W = 1, 2, 4, 8


class MazeRenderer:
    """mambo"""

    def __init__(self, config: Dict[str, Any]) -> None:
        """jambo"""
        self.config = config
        self.window_width: int = 800
        self.window_height: int = 800
        self.maze_width: int = config["WIDTH"]
        self.maze_height: int = config["HEIGHT"]
        self.entry: Tuple[int, int] = config["ENTRY"]
        self.exit: Tuple[int, int] = config["EXIT"]
        self.output_file: str = config["OUTPUT_FILE"]
        self.perfect: bool = config["PERFECT"]
        self.maze_area_width: int = 610
        self.maze_area_height: int = 610
        self.cell_size: int = 0
        self.wall_thickness: int = max(1, self.cell_size // 10)
        self.start_x: int = 0
        self.start_y: int = 0
        self.anim_index: int = 0
        self.path_anim_index: int = 0
        self.animation_frames: List[Tuple[int, int, int]] = []
        self.show_path: bool = False
        self.maze: List[List[int]] = []
        self.path: List[str] = []
        self.pattern_42: List[List[int]] = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
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
        self.color_path: int = 0xFFCCCCCC
        self.color_cell_bg: int = 0xFF888888

    def run_mlx_renderer(self, maze: List[List[int]]) -> None:
        """mambo"""
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
        self.reset_maze()
        self.draw_canvas(self.maze)
        self.mlx.mlx_mouse_hook(self.win_ptr, self.mouse_handler, None)
        self.mlx.mlx_key_hook(self.win_ptr, self.key_handler, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.close_handle, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.animation_step, None)
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
                                                 ' to exit')
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 722,
                                self.color_text, '3. Rotate themes (current - '
                                f'"{self.theme_name}")')
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 744,
                                self.color_text, '4. Exit')
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 766,
                                self.color_text, 'Choose one (1-4)')

    def reset_maze(self) -> None:
        """nambo"""
        # Calculate cell size as the largest size that fits the maze
        self.cell_size = min(
            (self.maze_area_width - self.wall_thickness * 2)
            // self.maze_width,
            (self.maze_area_height - self.wall_thickness * 2)
            // self.maze_height
        )
        self.wall_thickness = max(1, min(self.cell_size // 10, 5))
        # Calculate maze pixel dimensions and centered starting position
        # within the grey area
        maze_pixel_width: int = self.maze_width * self.cell_size
        maze_pixel_height: int = self.maze_height * self.cell_size
        self.start_x = max(
            self.wall_thickness, (self.maze_area_width - maze_pixel_width) // 2
        )
        self.start_y = max(
            self.wall_thickness,
            (self.maze_area_height - maze_pixel_height) // 2
        )
        if self.maze_width >= 13 or self.maze_height >= 13:
            self.start_x += 3
            self.start_y += 3
        self.maze = [[15] * self.maze_width for _ in range(self.maze_height)]

    def draw_cell(self, col: int, row: int, value: int) -> None:
        """lambo"""
        cell_x: int = self.start_x + (col * self.cell_size)
        cell_y: int = self.start_y + (row * self.cell_size)
        for py in range(self.cell_size):
            for px in range(self.cell_size):
                if self.size_line is not None and self.data is not None:
                    offset: int = (
                        ((cell_y + py) * self.size_line) +
                        ((cell_x + px) * 4)
                    )
                    self.data[offset:offset+4] = (
                        self.color_maze_area.to_bytes(4, 'little'))
        self.draw_walls(cell_x, cell_y, value)
        for py in range(self.wall_thickness, self.cell_size):
            for px in range(self.wall_thickness, self.cell_size):
                if self.size_line is not None and self.data is not None:
                    offset = (
                        ((cell_y + py) * self.size_line) +
                        ((cell_x + px) * 4)
                    )
                    self.data[offset:offset+4] = (
                        self.color_cell_bg.to_bytes(4, 'little'))
        if col > 0 and row > 0:
            above_left = self.maze[row - 1][col - 1]
            if bool(above_left & S) and bool(above_left & E):
                for wy in range(self.wall_thickness):
                    for wx in range(self.wall_thickness):
                        if self.size_line is not None \
                                and self.data is not None:
                            offset = (
                                ((cell_y + wy) * self.size_line) +
                                ((cell_x + wx) * 4)
                            )
                            self.data[offset:offset+4] = (
                                self.color_wall.to_bytes(4, 'little'))

    def animation_step(self, param: Any) -> int:
        """jambo"""
        if self.mlx is None:
            return 0
        if self.anim_index >= len(self.animation_frames):
            if self.show_path and self.path_anim_index < len(self.path):
                self.draw_path(self.start_x, self.start_y)
                self.path_anim_index += 1
                self.mlx.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr, self.image, 95, 45)
            return 0
        x, y, value = self.animation_frames[self.anim_index]
        self.maze[y][x] = value
        self.draw_cell(x, y, value)
        self.draw_42_pattern(
            self.start_x, self.start_y,
            self.maze_width, self.maze_height, self.pattern_42)
        self.draw_entry_exit(self.start_x, self.start_y)
        self.anim_index += 1
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.image, 95, 45)
        return 0

    def draw_walls(self, cell_x: int, cell_y: int, cell: int) -> None:
        """Draw walls for a single cell based on bitwise cell value."""
        north: bool = bool(cell & N)
        south: bool = bool(cell & S)
        east: bool = bool(cell & E)
        west: bool = bool(cell & W)
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
        for wy in range(self.wall_thickness):
            for wx in range(self.wall_thickness):
                if self.size_line is not None and self.data is not None:
                    offset = (
                        ((cell_y + self.cell_size + wy) * self.size_line) +
                        ((cell_x + self.cell_size + wx) * 4)
                    )
                    self.data[offset:offset+4] = (
                        self.color_wall.to_bytes(4, 'little'))

    def draw_maze(self, maze: List[List[int]]) -> None:
        """jambo"""
        for row in range(len(maze)):
            for col in range(len(maze[row])):
                cell_x: int = self.start_x + (col * self.cell_size)
                cell_y: int = self.start_y + (row * self.cell_size)
                cell: int = maze[row][col]
                self.draw_walls(cell_x, cell_y, cell)
        for row in range(len(maze)):
            for col in range(len(maze[row])):
                cell_x = self.start_x + (col * self.cell_size)
                cell_y = self.start_y + (row * self.cell_size)
                for py in range(self.wall_thickness, self.cell_size):
                    for px in range(self.wall_thickness, self.cell_size):
                        if self.size_line is not None \
                                and self.data is not None:
                            offset: int = (
                                ((cell_y + py) * self.size_line) +
                                ((cell_x + px) * 4)
                            )
                            self.data[offset:offset+4] = (
                                self.color_cell_bg.to_bytes(4, 'little'))
        # Draw 42 pattern if maze is large enough and store its grid position
        if self.maze_width >= 9 or self.maze_height >= 7:
            self.draw_42_pattern(
                self.start_x, self.start_y,
                self.maze_width, self.maze_height, self.pattern_42)
        self.draw_entry_exit(self.start_x, self.start_y)
        if self.show_path:
            self.draw_path(self.start_x, self.start_y)

    def draw_42_pattern(self, start_x: int, start_y: int,
                        len_maze_cols: int, len_maze_rows: int,
                        pattern_42: List[List[int]]) -> Tuple[int, int]:
        """Draw the '42' pattern using fully closed cells."""
        pattern_col = (len_maze_cols - len(pattern_42[0])) // 2
        pattern_row = (len_maze_rows - len(pattern_42)) // 2
        pattern_start_x = start_x + (pattern_col * self.cell_size)
        pattern_start_y = start_y + (pattern_row * self.cell_size)
        for row in range(len(pattern_42)):
            for col in range(len(pattern_42[row])):
                if pattern_42[row][col] == 1:
                    cell_x = pattern_start_x + (col * self.cell_size)
                    cell_y = pattern_start_y + (row * self.cell_size)
                    for py in range(self.wall_thickness, self.cell_size):
                        for px in range(self.wall_thickness, self.cell_size):
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
        themes: List[Dict[str, Any]] = [
            {
                "theme_name": "Dark",
                "color_window_bg": 0xFF000000,
                "color_maze_area": 0xFF666666,
                "color_wall": 0xFF000000,
                "color_pattern": 0xFF333333,
                "color_text": 0xFF888888,
                "color_path": 0xFFCCCCCC,
                "color_cell_bg": 0xFF888888
            },
            {
                "theme_name": "Negative",
                "color_window_bg": 0xFF808080,
                "color_maze_area": 0xFF5A5A5A,
                "color_wall": 0xFF000000,
                "color_pattern": 0xFF222222,
                "color_text": 0xFFCCCCCC,
                "color_path": 0xFFAAAAAA,
                "color_cell_bg": 0xFF444444
            },
            {
                "theme_name": "42",
                "color_window_bg": 0xFF0A0A1A,
                "color_maze_area": 0xFF27B0F5,
                "color_wall": 0xFF122840,
                "color_pattern": 0xFF333333,
                "color_text": 0xFFF5B027,
                "color_path": 0xFF00BFFF,
                "color_cell_bg": 0xFF3D6B8C
            }
        ]
        self.current_theme = (self.current_theme + 1) % len(themes)
        for key, value in themes[self.current_theme].items():
            if key != "name":
                setattr(self, key, value)

    def draw_entry_exit(self, start_x: int, start_y: int) -> None:
        """jambo"""
        entry_x: int = start_x + (self.entry[0] * self.cell_size)
        entry_y: int = start_y + (self.entry[1] * self.cell_size)
        exit_x: int = start_x + (self.exit[0] * self.cell_size)
        exit_y: int = start_y + (self.exit[1] * self.cell_size)
        for py in range(self.cell_size):
            for px in range(self.cell_size):
                if px < self.wall_thickness or py < self.wall_thickness:
                    continue
                if self.size_line is not None and self.data is not None:
                    entry_offset: int = (
                        ((entry_y + py) * self.size_line) +
                        ((entry_x + px) * 4)
                    )
                    self.data[entry_offset: entry_offset+4] = (
                        (0xFF00CC00).to_bytes(4, 'little'))
                    exit_offset: int = (
                        ((exit_y + py) * self.size_line) +
                        ((exit_x + px) * 4)
                    )
                    self.data[exit_offset: exit_offset+4] = (
                        (0xFFCC0000).to_bytes(4, 'little'))

    def draw_path(self, start_x: int, start_y: int) -> None:
        """hambo"""
        entry_x: int = start_x + (self.entry[0] * self.cell_size)
        entry_y: int = start_y + (self.entry[1] * self.cell_size)
        for step, cell in enumerate(self.path):
            if 0 < step <= self.path_anim_index:
                for py in range(self.cell_size):
                    for px in range(self.cell_size):
                        if px < self.wall_thickness \
                                or py < self.wall_thickness:
                            continue
                        if self.size_line is not None \
                                and self.data is not None:
                            offset: int = (
                                ((entry_y + py) * self.size_line) +
                                ((entry_x + px) * 4)
                            )
                            self.data[offset: offset+4] = (
                                (self.color_path).to_bytes(4, 'little'))
            if cell == 'E':
                entry_x += self.cell_size
            elif cell == 'S':
                entry_y += self.cell_size
            elif cell == 'W':
                entry_x -= self.cell_size
            elif cell == 'N':
                entry_y -= self.cell_size

    def mouse_handler(self, button, x, y, mystuff):
        print(f"Got mouse event! button {button} at {x},{y}.")

    def key_handler(self, keynum, mystuff):
        if keynum == 32:
            self.mlx.mlx_mouse_hook(self.win_ptr, None, None)
        if keynum in (52, 65430):
            self.mlx.mlx_loop_exit(self.mlx_ptr)
            print("You pressed 4 to exit - bye!")
        elif keynum in (51, 65435):
            self.rotate_themes()
            self.draw_canvas(self.maze)
        elif keynum in (50, 65433):
            self.show_path = not self.show_path
            if self.show_path:
                self.path_anim_index = 0
            self.draw_canvas(self.maze)
        elif keynum in (49, 65436):
            self.reset_maze()
            self.show_path = False
            self.anim_index = 0
            self.draw_canvas(self.maze)
        else:
            print(f"Got key {keynum}, and got my stuff back:")

    def close_handle(self, dummy):
        self.mlx.mlx_loop_exit(self.mlx_ptr)
