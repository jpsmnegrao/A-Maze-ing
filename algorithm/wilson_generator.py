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
                           for _ in range(self.height)]  # creating 2D list
        # the 0s in the list mean that they are full blocks and not paths yet
        self.sleep_timer: float = 0.05  # EDITABLE-changes time between outputs
        self.logo_cell: int = -42
        self.insert_logo()  # replaces 0s in grid list with logo markers
        self.N, self.E, self.S, self.W = 4, 8, 1, 2  # set direction meaning
        self.dir_x: dict = {self.E: 1, self.W: -1, self.N: 0, self.S: 0}
        self.dir_y: dict = {self.E: 0, self.W: 0, self.N: 1, self.S: -1}
        self.inverted: dict = {self.E: self.W, self.W: self.E, self.N: self.S,
                               self.S: self.N}
        self.marked_cell: int = 16  # used to confirm that cells are for path
        self.out_file: str = config["OUTPUT_FILE"]
        self.first: bool = True  # truthy to let init path be set from exit
        self.save_path: bool = True  # truthy to save init path only once
        self.init_path: list = []  # steps that will be taken for solution
        self.path_str: str = ""
        self.curr_grid: list = []  # keeps what the grid looks like in hexadec

    # Func to create the 42 logo cells. Gets a middle point of width & height
    # and then marks certain cells around it as -42 instead of 0 so that
    # these cells wont be edited or looped over later by walk()
    def insert_logo(self) -> None:
        maze_center: tuple = (int(self.width / 2), int(self.height / 2))
        base_logo: list = [
            [
                [maze_center[0] - 3,
                 maze_center[0] + 1, maze_center[0] + 2, maze_center[0] + 3],
                maze_center[1] - 2
                ],
            [
                [maze_center[0] - 3,
                 maze_center[0] + 3],
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
                self.grid[row[1]][x_vals] = self.logo_cell

    # draw maze func that returns the current state of the maze to print
    # this print_maze func is mostly useless now (it was used for testing)
    def print_maze(self, cell_x: int | None = None, cell_y: int | None = None,
                   path: list | None = None) -> None:
        sym_block: str = "#"
        sym_path: str = "+"
        sym_empty: str = "."
        sym_current_cell: str = "[]"
        sym_logo: str = "F"
        height_count: int = 0

        for y, row in enumerate(self.grid):
            for x, block in enumerate(row):
                if block & self.S == 0:
                    print(" __", end="")
                elif block & self.S != 0:
                    print(" ..", end="")
            print("")
            for x, block in enumerate(row):
                if block & self.W == 0:
                    print("||", end="")
                elif self.W != 0:
                    print("..", end="")

                symbol: str = sym_block
                if cell_x == x and cell_y == y:
                    symbol = sym_current_cell
                elif self.grid[y][x] < -10:
                    symbol = sym_logo
                elif block and self.marked_cell:
                    symbol = sym_empty
                elif path and (x, y) in path:
                    symbol = sym_path
                print(symbol, end="")

            height_count += 1
            print(f"||{height_count}")
            if height_count == self.height:
                for x, block in enumerate(row):
                    print(" __", end="")
        print("")

    # walk func that takes x y pos and then randomly choose directions to
    # repeatedly walk until one of the conds are met
    # this will draw and sleep between each new cell it has walked
    def walk(self) -> list:
        while True:  # constantly loops until path is found
            if self.first is True:  # get exit cell for the solution/first path
                cell_x, cell_y = self.exit[0], self.exit[1]
                self.first = False
            else:  # gets a random cell within the grid
                cell_y: int = random.randint(0, self.height - 1)
                cell_x: int = random.randint(0, self.width - 1)
            # when random cell has been changed or is logo then resets loop
            if self.grid[cell_y][cell_x] != 0:
                continue
            if self.grid[cell_y][cell_x] < -10:
                continue

            # keeps track of where it has been so it can reset to earlier cell
            # or so it can pass it to the loop that saves it for later
            walked: dict = {(cell_x, cell_y): 0}
            init_x, init_y = cell_x, cell_y
            searching = True
            path = []

            while searching is True:
                if (cell_x, cell_y) in path:
                    # resets path to earlier cell if it found its own path
                    backtrack_index: int = path.index((cell_x, cell_y))
                    path = path[0:backtrack_index + 1]
                else:  # add current cell to path tracker
                    path.append((cell_x, cell_y))

                self.save_to_file(None)  # change this to pass attempting path
                time.sleep(self.sleep_timer)

                searching = False  # pauses walking to find next direction
                for dir in random.sample((self.N, self.S, self.E, self.W), 4):
                    next_x = cell_x + self.dir_x[dir]
                    next_y = cell_y + self.dir_y[dir]
                    if 0 <= next_x and next_x < self.width:
                        if 0 <= next_y < self.height:
                            walked[(cell_x, cell_y)] = dir
                            if self.grid[next_y][next_x] != 0:
                                if self.grid[next_y][next_x] < -10:
                                    # 42 cell would be next, get new direction
                                    searching = True
                                    continue
                                # entry/maze path found, stop walking to save
                                break
                            # still looking for maze -> set next cell and
                            # start walking again
                            cell_x, cell_y = next_x, next_y
                            searching = True
                            break

            # set up to save the correct path that was found as a return
            path = []
            x, y = init_x, init_y
            while (x, y) in walked:
                dir = walked[(x, y)]
                if dir == 0:
                    break
                path.append((x, y, dir))  # maze gen will pickup x, y, dir set
                if self.save_path is True:  # saves the first path for later
                    self.init_path.append(dir)
                x, y = x + self.dir_x[dir], y + self.dir_y[dir]
            if self.save_path is True:  # makes sure first path isnt changed
                self.init_path.reverse()
                self.save_path = False
            return path

    # generate maze creates a base 2D list, gets total cells, then calls walk
    # to make the first move, then draw with time.sleep to take breaks
    # between loops.
    # once no cells remain, the maze can have a final return
    # and then calls save
    def generate_maze(self, filename: str | None) -> list:
        entry_x, entry_y = self.entry[0], self.entry[1]
        self.grid[entry_x][entry_y] = self.marked_cell
        remaining_cells = (self.width * self.height) - 21  # cells to change

        while remaining_cells > 0:
            for x, y, dir in self.walk():  # runs walk to get next path
                next_x, next_y = x + self.dir_x[dir], y + self.dir_y[dir]

                if self.grid[y][x] > -10:  # verify not 42 logo
                    print(f"-{dir}")
                    self.grid[y][x] |= dir  # assigns which wall was used
                    self.grid[y][x] |= self.marked_cell  # sets cell as a path
                if self.grid[next_y][next_x] > -10:  # verify not 42 logo
                    print(self.inverted[dir])
                    self.grid[next_y][next_x] |= self.inverted[dir]
                    self.grid[next_y][next_x] |= self.marked_cell

                self.save_to_file(None)
                time.sleep(self.sleep_timer)
                remaining_cells -= 1  # loop counting down

        # self.print_maze() - used for testing with terminal visuals
        self.save_to_file(filename)  # saves the final grid result

    # save maze function which reproduces the 2D list but replacing cells with
    # bit understanding of values
    def save_to_file(self, filename: str | None) -> list:
        save_list: list = []
        for y, row in enumerate(self.grid):  # creates hexadecimal list
            row_list: list = []
            for x, block in enumerate(row):
                if block == -42:
                    row_list.append("F")
                else:
                    cell_total: int = 0
                    if y == 0:
                        cell_total |= 1
                    elif block & self.N == 0:
                        cell_total |= 4
                    if x == 0:
                        cell_total |= 8
                    elif block & self.E == 0:
                        cell_total |= 2
                    if y == len(self.grid):
                        cell_total |= 1
                    elif block & self.S == 0:
                        cell_total |= 1
                    if x == len(row):
                        cell_total |= 8
                    elif block & self.W == 0:
                        cell_total |= 8
                    row_list.append(hex(cell_total)[2:].capitalize())
            save_list.append(row_list)

        if filename is None:  # save the current state of the grid as hexadecim
            self.curr_grid = save_list
        else:
            try:
                with open(filename, "w") as file:
                    for row in save_list:  # writes each cell in hexa to file
                        for cell in row:
                            file.write(cell)
                        file.write("\n")
                    file.write(f"\n{self.entry[0]},{self.entry[1]}")  # ENTRY
                    file.write(f"\n{self.exit[0]},{self.exit[1]}\n")  # EXIT
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


if __name__ == "__main__":  # pulls config and then initializes maze
    parser: dict = ParserReturn("config.txt")
    config: dict = parser.parse_config()
    wilson_maze = Maze(config)
    wilson_maze.generate_maze(config["OUTPUT_FILE"])
