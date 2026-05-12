"""Configuration parser for maze generation parameters.

Reads a KEY=VALUE config file, validates required fields (WIDTH, HEIGHT, ENTRY,
EXIT, OUTPUT_FILE, PERFECT) and optional ones (SEED and BONUS_42), and returns
a dict ready for the generator and renderer.
"""


from typing import Dict, Any, List


class ParserReturn:
    """Parser for maze configuration files.

    Reads and validates configuration parameters from a text file for maze
    generation.
    """

    def __init__(self, filename: str) -> None:
        """Initialize the configuration parser.

        Args:
            filename: Path to the configuration file
        """
        self.filename = filename

    def parse_config(self) -> Dict[str, Any]:
        """Parse and validate the complete maze configuration file.

        Reads the configuration file, parses all key-value pairs, validates
        required fields, and performs logical validation on the complete
        configuration.

        Returns:
            A dictionary containing all validated configuration parameters

        Raises:
            ValueError: If the file is not found, has invalid format, missing
                        required fields, or contains invalid values
        """
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
                        maze_config["WIDTH"] = self.parse_int(key, value)
                    elif key == "HEIGHT":
                        maze_config["HEIGHT"] = self.parse_int(key, value)
                    elif key == "ENTRY":
                        maze_config["ENTRY"] = self.parse_coords(key, value)
                    elif key == "EXIT":
                        maze_config["EXIT"] = self.parse_coords(key, value)
                    elif key == "OUTPUT_FILE":
                        maze_config["OUTPUT_FILE"] = self.parse_str(key, value)
                    elif key == "PERFECT":
                        maze_config["PERFECT"] = self.parse_bool(key, value)
                    elif key == "SEED":
                        if value:
                            maze_config["SEED"] = self.parse_int(key, value)
                    elif key == "BONUS_42":
                        maze_config["BONUS_42"] = self.parse_bool(key, value)
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
            width = maze_config["WIDTH"]
            height = maze_config["HEIGHT"]
            if width <= 8 or height <= 8:
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

    @staticmethod
    def parse_int(key: str, value: str) -> int:
        """Parse and validate an integer configuration value.

        Args:
            key: The configuration key name (e.g., 'WIDTH', 'HEIGHT', 'SEED')
            value: The raw string value to parse

        Returns:
            The parsed integer value

        Raises:
            ValueError: If value is not an integer or (for non-SEED keys) not
                        in range 4-1024
        """
        try:
            result: int = int(value)
        except ValueError:
            raise ValueError(f"{key} given to maze generator must be an "
                             "integer!")
        if key == "SEED":
            return result
        elif 4 <= result <= 1024:
            return result
        else:
            raise ValueError(f"Invalid {key.lower()} given to maze generator!")

    @staticmethod
    def parse_coords(key: str, value: str) -> tuple[int, int]:
        """Parse and validate coordinate configuration value.

        Args:
            key: The configuration key name (e.g., 'ENTRY', 'EXIT')
            value: The raw string value in format 'x,y'

        Returns:
            A tuple of (x, y) integer coordinates

        Raises:
            ValueError: If format is incorrect or values are not integers
        """
        coords: list[str] = value.split(',')
        if len(coords) != 2:
            raise ValueError(f"{key} format incorrect: x,y")
        try:
            x: int = int(coords[0].strip())
            y: int = int(coords[1].strip())
        except ValueError:
            raise ValueError(f"Invalid {key.lower()} point given to maze "
                             "generator!")
        return (x, y)

    @staticmethod
    def parse_str(key: str, value: str) -> str:
        """Parse and validate a string configuration value.

        Args:
            key: The configuration key name
            value: The raw string value to parse

        Returns:
            The validated string value

        Raises:
            ValueError: If the string is empty
        """
        filename: str = value.strip()
        if filename:
            return filename
        else:
            raise ValueError(f"Invalid {key.lower()} given to maze generator!")

    @staticmethod
    def parse_bool(key: str, value: str) -> bool:
        """Parse and validate a boolean configuration value.

        Args:
            key: The configuration key name (e.g., 'PERFECT', '42BONUS')
            value: The raw string value ('true' or 'false', case-insensitive)

        Returns:
            The parsed boolean value

        Raises:
            ValueError: If value is not 'true' or 'false'
        """
        perfect: str = value.strip().lower()
        if perfect in ("true", "false"):
            return perfect == "true"
        else:
            raise ValueError(
                f"Invalid value for {key.lower()}: must be true or false.")
