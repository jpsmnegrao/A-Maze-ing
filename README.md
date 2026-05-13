*This project has been created as part of the 42 curriculum by joshde-s and jpaim-so*

# A-Maze-ing

## Description

This project's objective is to implement a maze generator in Python that takes
a configuration file, generates a maze, possibly perfect (with a single path
between entrance and exit), and writes it to a file using a hexadecimal wall
representation.

It is also required to provide a visual representation of the maze and
organizing the code so that the generation logic can be reused later.

## Instructions

1. Download the repo
2. Install dependencies and build the mazegen package — `make install` (creates
   the matrix venv automatically)
3. Activate the virtual environment - `source matrix/bin/activate`
4. Run the script - `make run`
5. To rebuild the mazegen package from sources — `make wheel` - this produces a
   fresh mazegen-*.whl at the repo root.

You can change the maze configuration by altering the values in the
`config.txt` file.

## Resources

### References

- MiniLibX manuals provided in the project page — used as the main reference
  for MLX functions and rendering behavior
- [PEP 257](https://peps.python.org/pep-0257/) — docstring conventions
- [PEP 8](https://peps.python.org/pep-0008/) — Python style guide
- [Maze Algorithm's](https://en.wikipedia.org/wiki/Maze_generation_algorithm) — General maze generation information
    - [Loop-erased random walk](https://en.wikipedia.org/wiki/Loop-erased_random_walk) — Wilson's Algorithm

AI was used for:
- Reviewing docstrings and inline comments to meet PEP 257 and the project's
  documentation requirements
- Explaining MLX concepts (image buffers, byte order, pixel addressing) when
  the manual was unclear
- Debugging rendering issues such as missing wall corners and animation wipe
  behavior

The renderer code itself was written by hand. AI was used as a debugging and
documentation aid, with all generated suggestions reviewed and tested before
being kept.

## Additional Sections:

### Config File Structure

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

### Maze generation algorithm

#### The Wilson's Algorithm

The Wilson's algorithm, also known as loop-erased random walking, is a unique
        algorithm compared to many of the other maze generator algorithms as it
        focuses its randomization in a more structured manner. This is due to
        the fact that the algorithm begins by having 2 points within the space,
        it then repeatedly chooses a direction and then tries to move into the
        neighboring cell in that direction (as long as the neighboring cell is
        a valid cell). If the cell it tries to move into is a pathway that was
        created in the current walking step then the algorithm will stop
        walking, reset back to the point it collided with, and then start walking
        again. If the path instead finds the other point it is looking for then
        it will create the path by assigning which walls should be open to get to
        the point. The algorithm then repeatedly randomly picks cells that have
        not been turned into paths and tries to walk from there again but this
        time it will only create a path when it finds its way to a path that was
        previously created. This is repeatedly done until all valid cells have
        been walked from and there for all cells should have only 3 or less walls.

This algorithm works well compared to many other alogrithms as other algorithms
        can have a tendency to create very long corridors (backtracking algorithms)
        or a lot of dead ends (Prim's algorithm). Wilson's algorithm does have some
        downfalls of its own like for example it can take longer to generate larger
        mazes as it can take a varied amount of time to find the initial pathways.
        Wilson's algorithm can also be more difficult to implement as it can very
        easily try to walk outside of the maze, and therefore needs a lot of counter
        measures to prevent this from happening.

### Reusable Maze Generator

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

## Team and Project Management

### Roles

- **[joshde-s]** — maze generator (Wilson's algorithm implementation, output
  				   file format, 42 logo placement)
- **[jpaim-so]** — visual renderer (MLX-based display, animation, theme system,
  				   user input handling), parser (config file validation)

### Planning

Given we knew we were both going to be with limited availability over the first
weeks working on the project we decided to keep the work loosely divided rather
than setting hard deadlines. Jaime worked on the parser and the visual
representation while Naki worked on the maze generator and related algorithms.

We keep in touch regularly and in spite of not meeting in person during most of
the project's development we had great communication, we were able to
communicate issues we saw with each other's code (and our own) and overall
just had a very good vibe.

### What worked well

Jaime - I think in spite of not meeting in person for most of the project
		development it went quite well in terms of what could be expected.
		Limited availability meant of course that we could not meet in person
		but that was not a problem at all.

Naki -  Like Jaime mentioned, our team work and communication seemed to work
        really well. While personal life was happening, we both communicated
        proficiently to keep each other updated and informed. We also used
        git functionalities really well to give each other appropriate
        access to each others' work.

### What could be improved

Jaime - It's hard to pinpoint anything in specific when this collaboration
		worked so well remotely but I imagine if working together every now and
		then the communication of certain topics or issues found could have
		been quicker.

Naki -  To extend on the notion of working mostly remotely, I think more work
        from campus would have been useful as there were some issues in the way
        the systems would render on our personal devices compared to campus PCs.
        Both of using campus computers would help not just with working together
        but also to find these between different PC issues quicker.
        From the algorithm side, the algorithm itself automatically makes perfect
        mazes, so making more algorithms could be useful to show how imperfect
        mazes could look and how they would have to be managed differently.

### Tools

- Python 3 with type hints
- flake8 and mypy for linting and static type checking
- MiniLibX for the graphical renderer
- Git/GitHub for version control
- AI assistance for debugging and documentation (see Resources section)

### Bonus Features

The renderer implements several extra features beyond the mandatory requirements:

- **Animated maze rendering** — cells are drawn one at a time as the maze
  								loads, instead of appearing all at once.
- **Animated solution path** — when the path is toggled on, it draws
  							   progressively from entry to exit.
- **Multiple color themes** — three themes (Dark, Earth, 42) that can be
  							  cycled at runtime via keyboard.
- **Live maze regeneration** — pressing the regenerate key reruns the generator
  							   and reloads the maze without restarting the
							   program.
- **Quit maze functionality** — pressing 4 adds an easy way for the
                                user to quickly close the maze program.
- **42 logo unique flag**   — added an additional flag that can be used in the
                              config file to set BONUS_42 to be True or False.
                              This changes how the 42 pattern is shaped.

