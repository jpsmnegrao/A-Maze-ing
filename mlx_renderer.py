"""Visual maze renderer using the MiniLibX (MLX) library.

Reads a maze grid and solution path produced by the generator and displays
them in a window. Supports user interactions for regenerating the maze,
toggling the solution path, rotating between color themes and closing the
window.
"""


from typing import Dict, List, Tuple, Optional, Any
from mlx import Mlx
from algorithm.wilson_generator import Maze


# Direction bit values per project spec (N=1, E=2, S=4, W=8)
N, E, S, W = 1, 2, 4, 8


class MazeRenderer:
    """Visual maze renderer using the MiniLibX (MLX) library.

    Loads a maze grid and solution path from the generator output, draws them
    in an MLX window, and handles user input for regenerating, toggling the
    path, rotating themes and clsoing the window.
    """

    def __init__(self, config: Dict[str, Any], maze_gen: Maze) -> None:
        """Initialize renderer state from the parsed config dict.

        Stores maze dimensions, entry/exit, and output file path; sets up
        default rendering values, animation counters, and theme colors. MLX
        objects are not created here — they are initialized in
        run_mlx_renderer when the window is opened.
        """
        # Config and maze parameters from parser
        self.config = config
        self.maze_gen = maze_gen
        self.maze_width: int = config["WIDTH"]
        self.maze_height: int = config["HEIGHT"]
        self.entry: Tuple[int, int] = config["ENTRY"]
        self.exit: Tuple[int, int] = config["EXIT"]
        self.output_file: str = config["OUTPUT_FILE"]
        self.perfect: bool = config["PERFECT"]
        self.bonus_42: bool = config["BONUS_42"]
        # Window and maze drawing area dimensions in pixels
        self.window_width: int = 800
        self.window_height: int = 800
        self.maze_area_width: int = 610
        self.maze_area_height: int = 610
        # Cell sizing and starting offset (computed in reset_maze)
        self.cell_size: int = 0
        self.wall_thickness: int = max(1, self.cell_size // 10)
        self.start_x: int = 0
        self.start_y: int = 0
        # Animation counters and state
        self.anim_index: int = 0
        self.path_anim_index: int = 0
        self.animation_frames: List[Tuple[int, int, int]] = []
        self.show_path: bool = False
        # Maze grid and solution path loaded from output file
        self.maze: List[List[int]] = []
        self.path: List[str] = []
        if self.bonus_42:
            self.pattern_42: List[List[int]] = [
                [1, 0, 1, 0, 1, 1, 1],
                [1, 0, 1, 0, 0, 0, 1],
                [1, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 1, 1],
            ]
        else:
            self.pattern_42 = [
                [1, 0, 0, 0, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 1, 1],
            ]
        # MLX objects (initialized in run_mlx_renderer)
        # Python object that gives access to all MLX functions
        self.mlx: Optional[Mlx] = None
        # Internal MLX state needed by every MLX call
        self.mlx_ptr: Optional[Any] = None
        # The window MLX created on screen
        self.win_ptr: Optional[Any] = None
        # MLX image buffer for the maze
        self.image: Optional[Any] = None
        # Raw pixel bytes of the image
        self.data: Optional[Any] = None
        # Bits per pixel (4 bytes)
        self.bpp: Optional[Any] = None
        # Bytes per row of the image
        self.size_line: Optional[int] = None
        # The order MLX expects color bytes in (little-endian here)
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
        """Initialize MLX, build the window, and start the event loop.

        Sets up the MLX context, creates the window and the two image buffers
        (background and maze), wires up input/close/animation hooks, then
        enters mlx_loop which blocks until the window closes.
        """
        # Initialize MLX and create the main window
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        self.win_ptr = self.mlx.mlx_new_window(
                       self.mlx_ptr, self.window_width, self.window_height,
                       "A-Maze-ing"
                )
        # Background image buffer (window backdrop)
        self.bg_image = self.mlx.mlx_new_image(
            self.mlx_ptr, self.window_width, self.window_height)
        self.bg_data, _, self.bg_size_line, _ = (
            self.mlx.mlx_get_data_addr(self.bg_image))
        # Maze image buffer (cells, walls, path, entry/exit)
        self.image = self.mlx.mlx_new_image(
                     self.mlx_ptr, self.maze_area_width + 10,
                     self.maze_area_height + 10
            )
        self.data, self.bpp, self.size_line, self.iformat = (
            self.mlx.mlx_get_data_addr(self.image))
        # Compute cell sizing/offsets and draw the initial frame
        self.reset_maze()
        self.draw_canvas(self.maze)
        # Register input handlers and the per-frame animation callback
        self.mlx.mlx_key_hook(self.win_ptr, self.key_handler, None)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self.close_handle, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.animation_step, None)
        # Hand control to MLX (blocks until the window is closed)
        self.mlx.mlx_loop(self.mlx_ptr)

    def draw_canvas(self, maze: List[List[int]]) -> None:
        """Redraw the entire window: background, maze area, maze, and UI text.

        Fills the background image, fills the maze drawing area with the theme
        color, draws the maze on top, then pushes both images to the window and
        overlays the title and menu strings. Offset computes the byte position
        where row y starts. bg_size_line is bytes per row (3200 for an 800-wide
        image with 4 bytes per pixel).
        """
        if self.mlx is None:
            return
        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        # Wait for the window clear to commit before doing anything else
        self.mlx.mlx_sync(
            self.mlx_ptr, self.mlx.SYNC_WIN_COMPLETED, self.win_ptr)
        # Make sure the background image buffer is safe to write to
        self.mlx.mlx_sync(
            self.mlx_ptr, self.mlx.SYNC_IMAGE_WRITABLE, self.bg_image)
        # Fill the background image with the window background color
        if self.bg_size_line is not None \
                and self.bg_data is not None:
            row_bytes: bytes = (
                self.color_window_bg.to_bytes(4, 'little') * self.window_width)
            for y in range(self.window_height):
                offset: int = y * self.bg_size_line
                self.bg_data[offset:offset + len(row_bytes)] = row_bytes
        # Make sure the maze image buffer is safe to write to
        self.mlx.mlx_sync(
            self.mlx_ptr, self.mlx.SYNC_IMAGE_WRITABLE, self.image)
        # Fill the maze area image with the maze area color
        if self.size_line is not None \
                and self.data is not None:
            row_bytes = (
                self.color_maze_area.to_bytes(4, 'little') *
                (self.maze_area_width + 10)
            )
            for y in range(self.maze_area_height + 10):
                offset = y * self.size_line
                self.data[offset:offset + len(row_bytes)] = row_bytes
        # Render the maze cells, walls, 42 pattern, entry/exit, and path
        self.draw_maze(maze)
        # Push background and maze images to the window
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                         self.bg_image, 0, 0)
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                         self.image, 95, 45)
        # Force image blits to complete before drawing text
        self.mlx.mlx_sync(
            self.mlx_ptr, self.mlx.SYNC_WIN_COMPLETED, self.win_ptr)
        # Draw the title and menu strings on top
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 309, 15,
                                self.color_text, "=== A-Maze-ing ===")
        self.mlx.mlx_do_sync(self.mlx_ptr)
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 678,
                                self.color_text, '1. Regenerate maze')
        self.mlx.mlx_do_sync(self.mlx_ptr)
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 700,
                                self.color_text, '2. Show/hide path from entry'
                                                 ' to exit')
        self.mlx.mlx_do_sync(self.mlx_ptr)
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 722,
                                self.color_text, '3. Rotate themes (current - '
                                f'"{self.theme_name}")')
        self.mlx.mlx_do_sync(self.mlx_ptr)
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 744,
                                self.color_text, '4. Exit')
        self.mlx.mlx_do_sync(self.mlx_ptr)
        self.mlx.mlx_string_put(self.mlx_ptr, self.win_ptr, 100, 766,
                                self.color_text, 'Choose one (1-4)')
        self.mlx.mlx_do_sync(self.mlx_ptr)

    def reset_maze(self) -> None:
        """Compute cell sizing/offsets and reset the maze grid to all-walls.

        Picks the largest cell size that fits the configured maze dimensions
        inside the maze area, scales wall thickness to match, centers the maze
        within the area, and initializes self.maze with every cell at 0xF (all
        four walls closed).
        """
        # Largest cell size that fits the maze inside the drawing area
        self.wall_thickness = 1
        self.cell_size = min(
            (self.maze_area_width - self.wall_thickness * 2)
            // self.maze_width,
            (self.maze_area_height - self.wall_thickness * 2)
            // self.maze_height
        )
        # Scale wall thickness with cell size, clamped to 1-5 pixels
        self.wall_thickness = max(1, min(self.cell_size // 10, 5))
        # Center the maze within the drawing area computing top left corner
        maze_pixel_width: int = self.maze_width * self.cell_size
        maze_pixel_height: int = self.maze_height * self.cell_size
        self.start_x = max(
            self.wall_thickness, (self.maze_area_width - maze_pixel_width) // 2
        )
        self.start_y = max(
            self.wall_thickness,
            (self.maze_area_height - maze_pixel_height) // 2
        )
        # Nudge offset for larger mazes to compensate for centering drift
        if self.maze_width >= 13 or self.maze_height >= 13:
            self.start_x += 3
            self.start_y += 3
        # Reset grid: every cell with all four walls closed (0xF)
        self.maze = [[15] * self.maze_width for _ in range(self.maze_height)]

    def regenerate(self) -> None:
        """Run the generator and reload the maze grid and path."""
        # Fresh Maze instance — generator state isn't reusable
        self.maze_gen = Maze(self.config)
        self.maze_gen.sleep_timer = 0
        self.maze_gen.generate_maze(self.output_file)
        # Read the new grid from the output file
        new_grid: List[List[int]] = []
        with open(self.output_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    break
                new_grid.append([int(ch, 16) for ch in line])
            f.readline()
            f.readline()
            path_line: str = f.readline().strip()
        # Reload renderer state with the new path and animation frames
        self.path = list(path_line)
        self.animation_frames = [
            (col, row, new_grid[row][col])
            for row in range(len(new_grid))
            for col in range(len(new_grid[row]))
        ]
        # Reset animation counters and grid for redraw
        self.anim_index = 0
        self.path_anim_index = 0
        self.show_path = False
        self.reset_maze()

    def draw_cell(self, col: int, row: int, value: int) -> None:
        """Draw a single maze cell at (col, row) with its walls.

        Clears the cell area to the maze area color, draws the cell's walls
        based on the bitwise wall value, fills the inner area with the cell
        background color, and patches the top-left corner if the cell
        above-left has matching south and east walls.
        """
        # Pixel coordinates of the cell's top-left corner
        cell_x: int = self.start_x + (col * self.cell_size)
        cell_y: int = self.start_y + (row * self.cell_size)
        # Clear the cell area with the maze area background color
        if self.size_line is not None and self.data is not None:
            row_bytes: bytes = (
                self.color_maze_area.to_bytes(4, 'little') * self.cell_size)
            for py in range(self.cell_size):
                offset: int = ((cell_y + py) * self.size_line) + (cell_x * 4)
                self.data[offset:offset + len(row_bytes)] = row_bytes
        # Draw the four walls based on the bitwise value (N/E/S/W bits)
        self.draw_walls(cell_x, cell_y, value)
        # Fill the inner cell area (inside the walls) with the cell color
        if self.size_line is not None and self.data is not None:
            inner_width = self.cell_size - self.wall_thickness
            row_bytes = (
                self.color_cell_bg.to_bytes(4, 'little') * inner_width)
            for py in range(self.wall_thickness, self.cell_size):
                offset = (
                    ((cell_y + py) * self.size_line) +
                    ((cell_x + self.wall_thickness) * 4)
                )
                self.data[offset:offset + len(row_bytes)] = row_bytes
        # Patch the top-left corner pixel block when the diagonal neighbour
        # has both south and east walls (closes the wall intersection)
        if (col > 0 and row > 0
                and (bool(self.maze[row - 1][col - 1] & S)
                     or bool(self.maze[row - 1][col - 1] & E))) \
                or (col > 0 and bool(self.maze[row][col - 1] & N)) \
                or (row > 0 and bool(self.maze[row - 1][col] & W)) \
                or bool(value & N) \
                or bool(value & W):
            if self.size_line is not None and self.data is not None:
                row_bytes = (
                    self.color_wall.to_bytes(
                        4, 'little') * self.wall_thickness
                )
                for wy in range(self.wall_thickness):
                    offset = ((cell_y + wy) * self.size_line) + (cell_x * 4)
                    self.data[offset:offset + len(row_bytes)] = row_bytes

    def animation_step(self, param: Any) -> int:
        """Render one animation step per MLX loop tick.

        Draws the next maze cell from animation_frames if any remain. Once the
        maze is fully drawn and the path toggle is on, advances the path
        animation one cell at a time. Pushes the updated maze image to the
        window after each step.
        """
        if self.mlx is None:
            return 0
        # Maze fully drawn: advance the path animation if toggled on
        if self.anim_index >= len(self.animation_frames):
            if self.show_path and self.path_anim_index < len(self.path):
                self.draw_path(self.start_x, self.start_y)
                self.path_anim_index += 1
                self.mlx.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr, self.image, 95, 45)
            return 0
        # Draw the next maze cell from the animation queue
        x, y, value = self.animation_frames[self.anim_index]
        self.maze[y][x] = value
        self.draw_cell(x, y, value)
        # Redraw 42 pattern and entry/exit on top so they stay visible
        if self.maze_width > 8 and self.maze_height > 8:
            self.draw_42_pattern(
                self.start_x, self.start_y,
                self.maze_width, self.maze_height, self.pattern_42)
        self.draw_entry_exit(self.start_x, self.start_y)
        # Advance animation step and push the updated frame to the window
        self.anim_index += 1
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.image, 95, 45)
        return 0

    def draw_walls(self, cell_x: int, cell_y: int, cell: int) -> None:
        """Draw the four walls of a single cell from its bitwise value.

        Reads the N/E/S/W bits from cell and paints each closed wall as a
        wall_thickness-wide strip along the matching edge. South and east
        strips extend by wall_thickness so neighbouring cells share clean
        corners. A final block patches the bottom-right corner pixel.
        """
        # Decode which walls are closed
        north: bool = bool(cell & N)
        south: bool = bool(cell & S)
        east: bool = bool(cell & E)
        west: bool = bool(cell & W)
        if self.size_line is None or self.data is None:
            return
        wall_color_bytes: bytes = self.color_wall.to_bytes(4, 'little')
        # Paint a wall_thickness-wide strip along each closed wall's edge
        if north:
            row_bytes: bytes = wall_color_bytes * self.cell_size
            for wall_row in range(self.wall_thickness):
                offset: int = (
                    ((cell_y + wall_row) * self.size_line) + (cell_x * 4))
                self.data[offset:offset + len(row_bytes)] = row_bytes
        if south:
            row_bytes = wall_color_bytes * (self.cell_size +
                                            self.wall_thickness)
            for wall_row in range(self.wall_thickness):
                offset = (
                    ((cell_y + self.cell_size + wall_row) * self.size_line) +
                    (cell_x * 4)
                )
                self.data[offset:offset + len(row_bytes)] = row_bytes
        if west:
            col_bytes: bytes = wall_color_bytes * self.wall_thickness
            for y in range(cell_y, cell_y + self.cell_size):
                offset = (y * self.size_line) + (cell_x * 4)
                self.data[offset:offset + len(col_bytes)] = col_bytes
        if east:
            col_bytes = wall_color_bytes * self.wall_thickness
            for y in range(cell_y, cell_y + self.cell_size +
                           self.wall_thickness):
                offset = (y * self.size_line) + ((cell_x + self.cell_size) * 4)
                self.data[offset:offset + len(col_bytes)] = col_bytes

    def draw_maze(self, maze: List[List[int]]) -> None:
        """Draw the full maze: walls, interiors, 42 pattern, entry/exit, path.

        Walls are drawn first across the whole grid, then cell interiors are
        filled on top to clean up any overlap. The 42 pattern, entry and exit
        cells, and (if toggled) the solution path are drawn last.
        """
        # First pass: draw walls for every cell
        for row in range(len(maze)):
            for col in range(len(maze[row])):
                cell_x: int = self.start_x + (col * self.cell_size)
                cell_y: int = self.start_y + (row * self.cell_size)
                cell: int = maze[row][col]
                self.draw_walls(cell_x, cell_y, cell)
        # Second pass: fill cell interiors with the cell background color
        if self.size_line is not None and self.data is not None:
            inner_width: int = self.cell_size - self.wall_thickness
            row_bytes: bytes = (
                self.color_cell_bg.to_bytes(4, 'little') * inner_width)
            for row in range(len(maze)):
                for col in range(len(maze[row])):
                    cell_x = self.start_x + (col * self.cell_size)
                    cell_y = self.start_y + (row * self.cell_size)
                    for py in range(self.wall_thickness, self.cell_size):
                        offset: int = (
                            ((cell_y + py) * self.size_line) +
                            ((cell_x + self.wall_thickness) * 4)
                        )
                        self.data[offset:offset + len(row_bytes)] = row_bytes
        # Draw 42 pattern if maze is large enough and store its grid position
        if self.maze_width > 8 and self.maze_height > 8:
            self.draw_42_pattern(
                self.start_x, self.start_y,
                self.maze_width, self.maze_height, self.pattern_42)
        # Draw entry and exit, and the solution path if toggled on
        self.draw_entry_exit(self.start_x, self.start_y)
        if self.show_path:
            self.draw_path(self.start_x, self.start_y)

    def draw_42_pattern(self, start_x: int, start_y: int,
                        len_maze_cols: int, len_maze_rows: int,
                        pattern_42: List[List[int]]) -> Tuple[int, int]:
        """Draw the '42' pattern using fully closed cells.

        Centers the pattern on the maze grid, then fills the interior of each
        pattern cell (skipping wall pixels) with the pattern color. Pixels
        outside the maze area are skipped. Returns the pattern's top-left
        position in grid coordinates.
        """
        # Center the pattern within the maze grid
        pattern_col: int = (len_maze_cols // 2) - 3
        pattern_row: int = (len_maze_rows // 2) - 2
        pattern_start_x: int = start_x + (pattern_col * self.cell_size)
        pattern_start_y: int = start_y + (pattern_row * self.cell_size)
        # Fill the interior of each pattern cell marked with 1
        for row in range(len(pattern_42)):
            for col in range(len(pattern_42[row])):
                if pattern_42[row][col] == 1:
                    cell_x: int = pattern_start_x + (col * self.cell_size)
                    cell_y: int = pattern_start_y + (row * self.cell_size)
                    for py in range(self.wall_thickness, self.cell_size):
                        for px in range(self.wall_thickness, self.cell_size):
                            pixel_x: int = cell_x + px
                            pixel_y: int = cell_y + py
                            if self.size_line is not None \
                                    and self.data is not None:
                                if not (
                                        pixel_x < 0
                                        or pixel_y < 0
                                        or pixel_x > self.maze_area_width
                                        or pixel_y > self.maze_area_height
                                        ):

                                    offset: int = (
                                        pixel_y * self.size_line) + (pixel_x
                                                                     * 4)
                                    self.data[offset:offset+4] = (
                                        (self.color_pattern).to_bytes(4,
                                                                      'little')
                                    )
        return pattern_col, pattern_row

    def rotate_themes(self) -> None:
        """Cycle to the next color theme and update theme attributes."""
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
                "theme_name": "Earth",
                "color_window_bg": 0xFF808080,
                "color_maze_area": 0xFF2A9333,
                "color_wall": 0xFF1E1E52,
                "color_pattern": 0xFF1E3852,
                "color_text": 0xFF381E52,
                "color_path": 0xFF52381E,
                "color_cell_bg": 0xFF38521E
            },
            {
                "theme_name": "42",
                "color_window_bg": 0xFF0A0A1A,
                "color_maze_area": 0xFF27B0F5,
                "color_wall": 0xFF122840,
                "color_pattern": 0xFF333333,
                "color_text": 0xFFF5B027,
                "color_path": 0xCC253687,
                "color_cell_bg": 0xFF3D6B8C
            }
        ]
        # Advance to the next theme and apply its values to self
        self.current_theme = (self.current_theme + 1) % len(themes)
        for key, value in themes[self.current_theme].items():
            setattr(self, key, value)

    def draw_entry_exit(self, start_x: int, start_y: int) -> None:
        """Fill the entry cell with green and the exit cell with red."""
        # Pixel coordinates of the entry and exit cells
        entry_x: int = start_x + (self.entry[0] * self.cell_size)
        entry_y: int = start_y + (self.entry[1] * self.cell_size)
        exit_x: int = start_x + (self.exit[0] * self.cell_size)
        exit_y: int = start_y + (self.exit[1] * self.cell_size)
        if self.size_line is None or self.data is None:
            return
        inner_width: int = self.cell_size - self.wall_thickness
        entry_bytes: bytes = (0xFF00CC00).to_bytes(4, 'little') * inner_width
        exit_bytes: bytes = (0xFFCC0000).to_bytes(4, 'little') * inner_width
        # Fill cell interiors (skip wall pixels) with entry/exit colors
        for py in range(self.wall_thickness, self.cell_size):
            entry_offset: int = (
                ((entry_y + py) * self.size_line) +
                ((entry_x + self.wall_thickness) * 4)
            )
            self.data[entry_offset:entry_offset + len(entry_bytes)] = (
                entry_bytes)
            exit_offset: int = (
                ((exit_y + py) * self.size_line) +
                ((exit_x + self.wall_thickness) * 4)
            )
            self.data[exit_offset:exit_offset + len(exit_bytes)] = exit_bytes

    def draw_path(self, start_x: int, start_y: int) -> None:
        """Draw the solution path one cell at a time, animated.

        Starts at the entry, walks through self.path letter by letter, and
        fills each visited cell's interior with the path color up to
        path_anim_index. The entry cell itself is skipped (step 0) so its
        green color stays visible.
        """
        # Start at the entry cell's pixel position
        entry_x: int = start_x + (self.entry[0] * self.cell_size)
        entry_y: int = start_y + (self.entry[1] * self.cell_size)
        if self.size_line is None or self.data is None:
            return
        inner_width: int = self.cell_size - self.wall_thickness
        row_bytes: bytes = self.color_path.to_bytes(4, 'little') * inner_width
        # Walk the path, painting each cell up to the current animation index
        for step, cell in enumerate(self.path):
            if 0 < step <= self.path_anim_index:
                for py in range(self.wall_thickness, self.cell_size):
                    offset: int = (
                        ((entry_y + py) * self.size_line) +
                        ((entry_x + self.wall_thickness) * 4)
                    )
                    self.data[offset:offset + len(row_bytes)] = row_bytes
            # Advance the cursor to the next cell based on the direction letter
            if cell == 'E':
                entry_x += self.cell_size
            elif cell == 'S':
                entry_y += self.cell_size
            elif cell == 'W':
                entry_x -= self.cell_size
            elif cell == 'N':
                entry_y -= self.cell_size

    def key_handler(self, keynum: int, mystuff: Any) -> None:
        """Handle keypresses for the maze controls (1-4)."""
        if keynum in (49, 65436):
            self.regenerate()
            self.show_path = False
            self.anim_index = 0
            self.draw_canvas(self.maze)
        elif keynum in (50, 65433):
            self.show_path = not self.show_path
            if self.show_path:
                self.path_anim_index = 0
            self.draw_canvas(self.maze)
        elif keynum in (51, 65435):
            self.rotate_themes()
            self.draw_canvas(self.maze)
            # Force theme-change frame to fully render before next loop tick
            if self.mlx is not None:
                self.mlx.mlx_sync(
                    self.mlx_ptr, self.mlx.SYNC_WIN_COMPLETED, self.win_ptr)
        elif keynum in (52, 65430):
            if self.mlx is not None:
                self.mlx.mlx_loop_exit(self.mlx_ptr)
            print("You pressed 4 to exit - bye!")
        # Unmapped keys
        else:
            print(f"You pressed {keynum}, it's an unassigned key!")

    def close_handle(self, dummy: Any) -> None:
        """Handle the window close button by exiting the MLX loop."""
        if self.mlx is not None:
            self.mlx.mlx_loop_exit(self.mlx_ptr)
