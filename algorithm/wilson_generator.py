import random
import time
from typing import Any


class Maze_Handler:
    """
    Pulls info from config to create the base setup for the maze.
    """
    def __init__(self, config: dict[Any, int]):
        self.width: int = config["WIDTH"]
        self.height: int = config["HEIGHT"]
        self.entry: Any = config["ENTRY"]
        self.exit: Any = config["EXIT"]
        try:
            self.logo_bonus: int = config["BONUS_42"]
        except KeyError:
            print("Config parsing error: Missing keys for maze",
                  "generation: ['BONUS_42']")
            exit()
        if config.get("SEED") is not None:
            random.seed(config["SEED"])


class Maze(Maze_Handler):
    """
    Responsible for creating the maze based on the configuration input.

    Creates the base maze by filling all the empty cells.
    Repeatedly takes walks to create empty paths in the maze.
    Each time a walk is made the maze gets saved into a reusable variable.
    Once every cell in the maze is used it tries to save to the output file.
    """
    def __init__(self, config: dict[Any, int]):
        super().__init__(config)
        self.grid: list[list[int]] = [[0 for _ in range(self.width)]
                                      for _ in range(self.height)]
        self.sleep_timer: float = 0.05
        self.logo_cell: int = 0
        if config["WIDTH"] > 8 and config["HEIGHT"] > 8:
            self.logo_cell = -42
            try:
                self.insert_logo()
            except ValueError as alert:
                print(alert)
                exit()
        self.N, self.E, self.S, self.W = 4, 8, 1, 2
        self.dir_x: dict[int, int] = {self.E: 1, self.W: -1, self.N: 0,
                                      self.S: 0}
        self.dir_y: dict[int, int] = {self.E: 0, self.W: 0, self.N: 1,
                                      self.S: -1}
        self.inverted: dict[int, int] = {self.E: self.W, self.W: self.E,
                                         self.N: self.S, self.S: self.N}
        self.marked_cell: int = 16
        self.out_file: int = config["OUTPUT_FILE"]
        self.first: bool = True
        self.save_path: bool = True
        self.init_path: list[int] = []
        self.path_str: str = ""
        self.curr_grid: list[int] = []

    def insert_logo(self) -> None:
        """
        Uses the mid height and width point to create the 42 logo.
        """
        maze_center: tuple[int, int] = (int(self.width / 2),
                                        int(self.height / 2))
        base_logo: list[list[Any]] = []
        if self.logo_bonus is False:
            base_logo = [
                [
                    [maze_center[0] - 3,
                     maze_center[0] + 1, maze_center[0] + 2,
                     maze_center[0] + 3],
                    maze_center[1] - 2
                    ],
                [
                    [maze_center[0] - 3,
                     maze_center[0] + 3],
                    maze_center[1] - 1
                    ],
                [
                    [maze_center[0] - 3, maze_center[0] - 2,
                     maze_center[0] - 1,
                     maze_center[0] + 1, maze_center[0] + 2,
                     maze_center[0] + 3],
                    maze_center[1]
                    ],
                [
                    [maze_center[0] - 1,
                     maze_center[0] + 1],
                    maze_center[1] + 1
                    ],
                [
                    [maze_center[0] - 1,
                     maze_center[0] + 1, maze_center[0] + 2,
                     maze_center[0] + 3],
                    maze_center[1] + 2
                    ]
            ]
        else:
            base_logo = [
                [
                    [maze_center[0] - 3, maze_center[0] - 1,
                     maze_center[0] + 1, maze_center[0] + 2,
                     maze_center[0] + 3],
                    maze_center[1] - 2
                    ],
                [
                    [maze_center[0] - 3, maze_center[0] - 1,
                     maze_center[0] + 3],
                    maze_center[1] - 1
                    ],
                [
                    [maze_center[0] - 3, maze_center[0] - 2,
                     maze_center[0] - 1,
                     maze_center[0] + 1, maze_center[0] + 2,
                     maze_center[0] + 3],
                    maze_center[1]
                    ],
                [
                    [maze_center[0] - 1,
                     maze_center[0] + 1],
                    maze_center[1] + 1
                    ],
                [
                    [maze_center[0] - 1,
                     maze_center[0] + 1, maze_center[0] + 2,
                     maze_center[0] + 3],
                    maze_center[1] + 2
                    ]
            ]

        for row in base_logo:
            for x_vals in row[0]:
                self.grid[row[1]][x_vals] = self.logo_cell
        if self.grid[self.exit[1]][self.exit[0]] == -42:
            raise ValueError("Exit point within 42 pattern!")
        elif self.grid[self.entry[1]][self.entry[0]] == -42:
            raise ValueError("Entry point within 42 pattern!")

    def walk(self) -> list[Any]:
        """
        Repeatedly finds possible paths through random choices.

        Either starting at the exit point or at a randomly chosen cell this
        function repeatedly loops through the 4 possible directions to select
        the next cell to move into. If the loop encounters itself, out of maze
        walls, or the 42 cells it will reset itself to that earlier cell in
        the path. However if it finds the entrance or a previously saved path,
        it will return the cells it visited and directions to get to that cell.
        """
        while True:
            if self.first is True:
                cell_x, cell_y = self.exit[0], self.exit[1]
                self.first = False
            else:
                cell_y = random.randint(0, self.height - 1)
                cell_x = random.randint(0, self.width - 1)
            if self.grid[cell_y][cell_x] != 0:
                continue
            if self.grid[cell_y][cell_x] < -10:
                continue

            walked: dict[Any, int] = {(cell_x, cell_y): 0}
            init_x, init_y = cell_x, cell_y
            searching = True
            path: list[Any] = []

            while searching is True:
                if (cell_x, cell_y) in path:
                    backtrack_index: int = path.index((cell_x, cell_y))
                    path = path[0:backtrack_index + 1]
                else:
                    path.append((cell_x, cell_y))

                self.save_to_file(None)
                time.sleep(self.sleep_timer)

                searching = False
                for dir in random.sample((self.N, self.S, self.E, self.W), 4):
                    next_x = cell_x + self.dir_x[dir]
                    next_y = cell_y + self.dir_y[dir]
                    if 0 <= next_x and next_x < self.width:
                        if 0 <= next_y < self.height:
                            walked[(cell_x, cell_y)] = dir
                            if self.grid[next_y][next_x] != 0:
                                if self.grid[next_y][next_x] < -10:
                                    searching = True
                                    continue
                                break
                            cell_x, cell_y = next_x, next_y
                            searching = True
                            break

            path = []
            x, y = init_x, init_y
            while (x, y) in walked:
                dir = walked[(x, y)]
                if dir == 0:
                    break
                path.append((x, y, dir))
                if self.save_path is True:
                    self.init_path.append(dir)
                x, y = x + self.dir_x[dir], y + self.dir_y[dir]
            if self.save_path is True:
                self.init_path.reverse()
                self.save_path = False
            return path

    def generate_maze(self, filename: str | None) -> None:
        """
        Recreates the 2D grid list to create the final maze with its walls.

        Starts by using the walk function to get a path between entry and exit.
        It then repeatedly calls walk to create more paths until all cells have
        been used, thus creating a wall setup that can be reused later.
        """
        entry_x, entry_y = self.entry[1], self.entry[0]
        self.grid[entry_x][entry_y] = self.marked_cell
        if self.logo_cell == -42:
            if self.logo_bonus is True:
                remaining_cells = (self.width * self.height) - 21
            else:
                remaining_cells = (self.width * self.height) - 19
        else:
            remaining_cells = (self.width * self.height) - 1

        while remaining_cells > 0:
            for x, y, dir in self.walk():
                next_x, next_y = x + self.dir_x[dir], y + self.dir_y[dir]

                if self.grid[y][x] > -10:
                    self.grid[y][x] |= dir
                    self.grid[y][x] |= self.marked_cell
                if self.grid[next_y][next_x] > -10:
                    self.grid[next_y][next_x] |= self.inverted[dir]
                    self.grid[next_y][next_x] |= self.marked_cell

                self.save_to_file(None)
                time.sleep(self.sleep_timer)
                remaining_cells -= 1

        self.save_to_file(filename)

    def save_to_file(self, filename: str | None) -> list[str]:
        """
        Turns the 2D grid into a 2D hexadecimal list and string.
        """
        save_list: list[Any] = []
        for y, row in enumerate(self.grid):
            row_list: list[str] = []
            for x, block in enumerate(row):
                if block == -42:
                    row_list.append("F")
                else:
                    cell_total: int = 0
                    if y == len(self.grid):
                        cell_total |= 4
                    elif block & self.N == 0:
                        cell_total |= 4
                    if x == len(row):
                        cell_total |= 2
                    elif block & self.E == 0:
                        cell_total |= 2
                    if y == 0:
                        cell_total |= 1
                    elif block & self.S == 0:
                        cell_total |= 1
                    if x == 0:
                        cell_total |= 8
                    elif block & self.W == 0:
                        cell_total |= 8
                    row_list.append(hex(cell_total)[2:].capitalize())
            save_list.append(row_list)

        self.curr_grid = save_list
        if filename is not None:
            try:
                with open(filename, "w") as file:
                    for row in save_list:
                        for cell in row:
                            file.write(f"{cell}")
                        file.write("\n")
                    file.write(f"\n{self.entry[0]},{self.entry[1]}")
                    file.write(f"\n{self.exit[0]},{self.exit[1]}\n")
                    dir_letter: str = ""
                    for dir in self.init_path:
                        if dir == 1:
                            dir_letter = "S"
                        elif dir == 2:
                            dir_letter = "E"
                        elif dir == 4:
                            dir_letter = "N"
                        elif dir == 8:
                            dir_letter = "W"
                        file.write(dir_letter)
                    file.write("\n")
            except FileNotFoundError:
                print("File not found to save to!")
        return save_list
