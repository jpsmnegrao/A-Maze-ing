This project has been created as part of the 42 curriculum by <login1>[, <login2>[, <login3>[...]]].

“Description” section that clearly presents the project, including its goal and a brief overview.

“Resources” section listing classic references related to the topic (documentation, articles, tutorials, etc.), as well as a description of how AI was used — specifying for which tasks and which parts of the project.

➠ Additional sections may be required depending on the project (e.g., usage
examples, feature list, technical choices, etc.).

======================

Required additions:

• The complete structure and format of your config file.
• The maze generation algorithm you chose.
• Why you chose this algorithm.
• What part of your code is reusable, and how.
• Your team and project management with:
◦ The roles of each team member.
◦ Your anticipated planning and how it evolved until the end
◦ What worked well and what could be improved
◦ Have you used any specific tools? Which ones?
If you implement advanced features (multiple algorithms, display options)

============================

Project todos:

1. ~~Project structure (Makefile, requirements.txt, venv, .gitignore, README.md)~~
2. ~~Parse config.txt -> seed, width, height, etc.~~
3. Maze generation -> algorithm + seed reproducibility - DFS
4. Maze rendering -> MLX window
5. Maze solving -> pathfinding - BFS
6. Test writing -> pytest
7. Package setup -> mazegen-*.whl

#1 (13/04) - project start
#2 (14/04) - made most of the parser, needs breaking down in smaller functions
#3 (15/04) - broke parser into int, coords, str and bool processors
           - started toml file for package setup
           - started tests folder, wrote comprehensive tests covering valid
             configs, missing fields, invalid formats, and edge cases
#4 (16/04) - got project partner, divided workload, started looking into MLX 


1. ~~Create basic project structure, repo, read PDF,~~ decide on algorithms and
   what to implement, work division.
2. [x] Parser programming
3. Maze generation - DFS
4. Maze solving - BFS
5. Visual representation - MLX Library
6. Coded Makefile
7. Created requirements.txt and decided on dependencies to use
