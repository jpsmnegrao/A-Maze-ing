"""
Module: test_config
Pytest script to test config parsing.
"""

from config import ParserReturn


def test_parse_valid_config() -> None:
    """mambo"""
    parser = ParserReturn("config.txt")
    result = parser.parse_config()
    assert isinstance(result["WIDTH"], int)
    assert isinstance(result["HEIGHT"], int)
