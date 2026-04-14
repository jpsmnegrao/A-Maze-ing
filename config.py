"""
Version 2.1
Module: config
Configuration parser for maze generation parameters.
"""


from typing import Dict, Any, List


class ParserReturn:
    """mambo"""

    def __init__(self, filename: str) -> None:
        """jambo"""
        self.filename = filename

    def parse_config(self) -> Dict[str, Any]:
        """jambo"""
        maze_config: Dict[str, Any] = {}
        try:
            with open(self.filename, 'r') as configs:
                for line in configs:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key_value: List[str] = line.split('=')
                    if len(key_value) != 2:
                        raise ValueError("Invalid config line format!")
                    key: str = key_value[0].strip().upper()
                    value: str = key_value[1].strip()
                    if key in maze_config:
                        raise ValueError(f"Duplicate key found: {key}")
                    if key == "WIDTH":
                        try:
                            width: int = int(value)
                            if 4 <= width <= 1024:
                                maze_config["WIDTH"] = width
                            else:
                                raise ValueError("Invalid width given to maze "
                                                 "generator!")
                        except ValueError:
                            raise ValueError("Width given to maze generator "
                                             "must be an integer!")
                    elif key == "HEIGHT":
                        try:
                            height: int = int(value)
                            if 4 <= height <= 1024:
                                maze_config["HEIGHT"] = height
                            else:
                                raise ValueError("Invalid height given to maze"
                                                 " generator!")
                        except ValueError:
                            raise ValueError("Height given to maze generator "
                                             "must be an integer!")
                    elif key == "ENTRY":
                        try:
                            parts: list[str] = value.split(',')
                            if len(parts) != 2:
                                raise ValueError("ENTRY format incorrect: x,y")
                            x: int = int(parts[0].strip())
                            y: int = int(parts[1].strip())
                            maze_config["ENTRY"] = (x, y)
                        except ValueError:
                            raise ValueError("Invalid entry point given to "
                                             "maze generator!")
                    elif key == "EXIT":
                        try:
                            parts = value.split(',')
                            if len(parts) != 2:
                                raise ValueError("EXIT format incorrect: x,y")
                            x = int(parts[0].strip())
                            y = int(parts[1].strip())
                            maze_config["EXIT"] = (x, y)
                        except ValueError:
                            raise ValueError("Invalid exit point given to "
                                             "maze generator!")
                    elif key == "OUTPUT_FILE":
                        filename: str = value.strip()
                        if filename:
                            maze_config["OUTPUT_FILE"] = filename
                        else:
                            raise ValueError("Invalid filename given to maze "
                                             "generator!")
                    elif key == "PERFECT":
                        perfect: str = value.strip().lower()
                        if perfect in ("true", "false"):
                            maze_config["PERFECT"] = perfect == "true"
                        else:
                            raise ValueError("Invalid maze perfection "
                                             "indication given to maze "
                                             "generator!")
                    else:
                        raise ValueError(f"Unknown key found: {key}")
            required_fields: List[str] = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                                          "OUTPUT_FILE", "PERFECT"]
            missing_fields: List[str] = [field for field in required_fields if
                                         field not in maze_config]
            if missing_fields:
                raise ValueError("Missing keys for maze generation: "
                                 f"{missing_fields}")
            if maze_config["ENTRY"] == maze_config["EXIT"]:
                raise ValueError("Entry and Exit points cannot be the same!")
            if width < 11 or height < 9:
                print("Warning: Maze is not big enough for 42 pattern.")
            entry_x, entry_z = maze_config["ENTRY"]
            exit_x, exit_z = maze_config["EXIT"]
            if not (0 <= entry_x < width and 0 <= entry_z < height):
                raise ValueError("Entry point outside maze bounds.")
            if not (0 <= exit_x < width and 0 <= exit_z < height):
                raise ValueError("Exit point outside maze bounds.")
            return maze_config
        except FileNotFoundError:
            raise ValueError(f"Config file '{self.filename}' not found")
        except Exception as error:
            raise ValueError(f"Config parsing error: {error}")
