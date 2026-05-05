*This project has been created as part of the 42 curriculum by joshde-s and jpaim-so*

# A-Maze-ing

## Description

This project's objective is to implement a maze generator in Python that takes a
configuration file, generates a maze, possibly perfect (with a single path
between entrance and exit), and writes it to a file using a hexadecimal wall
representation.

It is also required to provide a visual representation of the maze and
organizing the code so that the generation logic can be reused later.

## Instructions

1. Download the repo
2. Create a fresh virtual environment - `python3 -m venv venv`
3. Activate the virtual environment - `source venv/bin/activate`
4. Install project dependencies - `make install`
5. Run the script - `python3 a_maze_ing.py config.txt`

You can change the maze configuration by altering the values in the
`config.txt` file.

## Resources

### References

- MiniLibX manuals provided in the project page — used as the main reference
  for MLX functions and rendering behavior
- [PEP 257](https://peps.python.org/pep-0257/) — docstring conventions
- [PEP 8](https://peps.python.org/pep-0008/) — Python style guide

AI was used for:
- Reviewing docstrings and inline comments to meet PEP 257 and the project's
  documentation requirements
- Explaining MLX concepts (image buffers, byte order, pixel addressing) when
  the manual was unclear
- Debugging rendering issues such as missing wall corners and animation wipe
  behavior
- Giving suggestions for pytest test cases for the parser, generator output
  format, and renderer logic, code review and assistance in debugging issues
  found (code not submitted as part of the repository for the project)

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

- `SEED` — integer seed for reproducible generation. If omitted, the maze is
		   randomized at each run.

Example:

```
WIDTH=20
HEIGHT=15
ENTRY=1,0
EXIT=18,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

### Maze generation algorithm

• The maze generation algorithm you chose.
• Why you chose this algorithm.

### Reusable Maze Generator

• What part of your code is reusable, and how.

## Team and Project Management

### Roles

- **[joshde-s]** — maze generator (Wilson's algorithm implementation, output
  				   file format, 42 logo placement)
- **[jpaim-so]** — visual renderer (MLX-based display, animation, theme system,
  				   user input handling), parser (config file validation), test
				   suite with AI assistance

### Planning

We made no specific plans regarding deadlines as we were both going to be with
limited availability over the last couple of weeks. We keep in touch regularly
and in spite of not meeting in person during most of the project's development
we had great communication, we were able to communicate issues we saw with each
other's code (and our own) and overall just had a very good vibe.

### What worked well

Jaime - I think in spite of not meeting in person for most of the project
		development it went quite well in terms of what could be expected.
		Limited availability meant of course that we could not meet in person
		but that was not a problem at all.

### What could be improved

Jaime - It's hard to pinpoint anything in specific when this collaboration
		worked so well remotely but I imagine if working together every now and
		then the communication of certain topics or issues found could have
		been quicker.


### Tools

- Python 3 with type hints
- pytest for unit and integration testing
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
- **Multiple color themes** — three themes (Dark, Negative, 42) that can be
  							  cycled at runtime via keyboard.
- **Live maze regeneration** — pressing the regenerate key reruns the generator
  							   and reloads the maze without restarting the
							   program.
