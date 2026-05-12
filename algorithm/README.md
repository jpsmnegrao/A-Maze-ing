*This project has been created as part of the 42 curriculum by joshde-s and jpaim-so*

# A-Maze-ing

## Config File Structure

The configuration file is a plain text file passed as the only argument to the
program. Each line follows the format `KEY=VALUE`. Lines starting with `#` are
treated as comments and ignored, as are empty lines.

The following keys are required:

- `WIDTH` — maze width in cells (integer, 4–1024)
- `HEIGHT` — maze height in cells (integer, 4–1024)
- `ENTRY` — entry coordinates as `x,y`
- `EXIT` — exit coordinates as `x,y`, must be different from `ENTRY` and within
           bounds
- `OUTPUT_FILE` — filename where the generated maze is written
- `PERFECT` — `True` or `False`, whether the maze should be perfect (single
  		      path between entry and exit)

Optional:

- `SEED` — integer seed for reproducible generation. If no value is given the
  		   maze is randomized at each run.
- `BONUS_42` — bool check that when set to True will change the 4 in the 42
               logo to have an extra 2 cells. This can add a lot of variation
               to the maze while still using SEED and the same config setup.

Example:

```
WIDTH=20
HEIGHT=15
ENTRY=1,0
EXIT=18,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
BONUS_42=True
```

## Reusable Maze Generator

The Wilson's maze generator is built directly through an original Python Class
        called Maze, which along its generation repeatedly saves multiple
        different states that can be reused depending on the situation that is
        required of it.

- Create a Maze class instance to pull the below reusable variables.
    (ex. small_maze = Maze("config.txt")).
- curr_grid is one of the most reusable parts of this generator.
    - An instance of a maze can be created and then using maze_instance.curr_grid
            will give the user access to the current hexadecimal information for
            each cell. This helps to give constant updates as to what the maze
            looks like as it is being walked and once the maze has finished being
            generated, it can then directly be used to reproduce the maze by decoding
            the hexadecimal into walls for each cell. For example a 3 would mean the
            cell has its north and east walls both closed (this comes from the binary
            of 0011). By decoding 1 for North, 2 for East, 4 for South and 8 for West,
            this can easily be reused to recreate the maze in any visual format, or
            even use it to create lists to then code further logic into.
- init_path is a useful default saved path which is created once the first path has
        been found and created. This path can be used to show the solution to the
        maze (how to get from Entry to Exit following N, E, S, W commands) or can
        be used to show the initial setup of the maze itself.
- path_str is the variable that holds the N, E, S, W steps and can be accessed
        once the inital path has been created. This can be easier to use than
        the init_path as it is more readable than the hexadecimal code.
- The save_to_file method can be very useful too as once the maze has been fully
        generated, it then saves the hexadecimal structure for the maze into a
        specified file. This can then be read to recreate the maze, its solution
        path, as well as the entry and exit positions.
- sleep_timer can be rewritten to have a different value, this will change how
        quickly or slowly the maze takes to generate as well as how quickly the
        previous variables are returned, thus making it more reusable as changing
        this value can change how the maze is generated based on user preference.
