import random
from config import ParserReturn
import time


class Maze_Handler:
    """
    Pulls info from config to create the base setup for the maze
    """
    def __init__(self, config: dict):
        self.width: int = config["WIDTH"]
        self.height: int = config["HEIGHT"]
        self.entry: tuple = config["ENTRY"]
        self.exit: tuple = config["EXIT"]
        if config.get("SEED") is not None:
            random.seed(config["SEED"])


class Maze(Maze_Handler):
    """
    Responsible for:
    - taking in the config,
    - creating the base maze without empty cells,
    - then repeatedly takes walks to create empty paths in the maze,
    - each time a walk is made the maze gets redrawn,
    - finally the maze is saved to a requested output file
    """
    def __init__(self, config: dict):
        super().__init__(config)
        self.grid: list = [[0 for _ in range(self.width)]
                           for _ in range(self.height)]
        self.insert_logo()
        self.N, self.S, self.E, self.W = 1, 2, 4, 8
        self.dir_x: dict = {self.E: 1, self.W: -1, self.N: 0, self.S: 0}
        self.dir_y: dict = {self.E: 0, self.W: 0, self.N: 1, self.S: -1}
        self.inverted: dict = {self.E: self.W, self.W: self.E, self.N: self.S,
                               self.S: self.N}
        self.marked_cell: int = 16
        self.out_file: str = config["OUTPUT_FILE"]
        self.first = True

    def insert_logo(self) -> None:
        maze_center: tuple = (int(self.width / 2), int(self.height / 2))
        base_logo: list = [
            [
                [maze_center[0] - 3,
                 maze_center[0] + 1, maze_center[0] + 2, maze_center[0] + 3],
                maze_center[1] - 2
                ],
            [
                [maze_center[0] - 3, maze_center[0] + 3],
                maze_center[1] - 1
                ],
            [
                [maze_center[0] - 3, maze_center[0] - 2, maze_center[0] - 1,
                 maze_center[0] + 1, maze_center[0] + 2, maze_center[0] + 3],
                maze_center[1]
                ],
            [
                [maze_center[0] - 1,
                 maze_center[0] + 1],
                maze_center[1] + 1
                ],
            [
                [maze_center[0] - 1,
                 maze_center[0] + 1, maze_center[0] + 2, maze_center[0] + 3],
                maze_center[1] + 2
                ]
        ]

        for row in base_logo:
            for x_vals in row[0]:
                self.grid[x_vals][row[1]] = 42

    # draw maze func that returns the current state of the maze to print
    def print_maze(self, cell_x: int | None = None, cell_y: int | None = None,
                   path: list | None = None) -> None:
        sym_block: str = "#"
        sym_path: str = "+"
        sym_empty: str = " "
        sym_current_cell: str = "[]"
        sym_logo: str = "F"
        width_count: int = 0

        for y, row in enumerate(self.grid):
            for x, block in enumerate(row):
                symbol: str = sym_block
                if cell_x == x and cell_y == y:
                    symbol = sym_current_cell
                elif block & self.marked_cell:
                    symbol = sym_empty
                elif path and (x, y) in path:
                    symbol = sym_path
                elif self.grid[x][y] == 42:
                    symbol = sym_logo
                print(symbol, end="")
            width_count += 1
            print(width_count)
            if width_count == self.width:
                width_count = 0
                print("")
        print("")

    # walk func that takes x y pos and then randomly choose directions to
    # repeatedly walk until one of the conds are met
    # this will draw and sleep between each new cell it has walked
    def walk(self) -> list:
        while True:
            if self.first is True:
                cell_y, cell_x = self.exit[0], self.exit[1]
                self.first = False
            else:
                cell_y: int = random.randint(0, self.height - 1)
                cell_x: int = random.randint(0, self.width - 1)
            if self.grid[cell_y][cell_x] != 0:
                continue

            walked: dict = {(cell_x, cell_y): 0}
            init_x, init_y = cell_x, cell_y
            searching = True
            path = []

            while searching is True:
                if (cell_x, cell_y) in path:
                    backtrack_index: int = path.index((cell_x, cell_y))
                    path = path[0:backtrack_index + 1]
                else:
                    path.append((cell_x, cell_y))

                self.print_maze(cell_x, cell_y, path)
                time.sleep(0.01)

                searching = False
                for dir in random.sample((self.N, self.S, self.E, self.W), 4):
                    next_x = cell_x + self.dir_x[dir]
                    next_y = cell_y + self.dir_y[dir]
                    if 0 <= next_x and next_x < self.width:
                        if 0 <= next_y < self.height:
                            walked[(cell_x, cell_y)] = dir
                            if self.grid[next_y][next_x] != 0:
                                if self.grid[next_y][next_x] != 42:
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
                x, y = x + self.dir_x[dir], y + self.dir_y[dir]
            return path

    # generate maze creates a base 2D list, gets total cells, then calls walk
    # to make the first move, then draw with time.sleep to take breaks
    # between loops.
    # once no cells remain, the maze can have a final return
    # and then calls save
    def generate_maze(self) -> list:
        entry_x, entry_y = self.entry[0], self.entry[1]
        self.grid[entry_x][entry_y] = self.marked_cell
        remaining_cells = self.width * self.height - 20

        while remaining_cells > 0:
            for x, y, dir in self.walk():
                next_x, next_y = x + self.dir_x[dir], y + self.dir_y[dir]

                self.grid[y][x] |= dir
                self.grid[y][x] |= self.marked_cell
                self.grid[next_y][next_x] |= self.inverted[dir]
                self.grid[next_y][next_x] |= self.marked_cell

                self.print_maze()
                time.sleep(0.01)
                remaining_cells -= 1

        self.print_maze()
        self.save_to_file()

    # save maze function which reproduces the 2D list but replacing cells with
    # bit understanding of values
    def save_to_file(self) -> None:
        # try:
        # with open(self.out_file, "w") as file:
        # file.write(self.grid)
        # except FileNotFoundError:
        # print("File not found to save to!")
        print(self.grid)


if __name__ == "__main__":
    parser: dict = ParserReturn("config.txt")
    config: dict = parser.parse_config()
    wilson_maze = Maze(config)
    wilson_maze.generate_maze()
