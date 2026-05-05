"""
Module: test_config
Pytest script to test config parsing.
"""


from typing import Dict, Any
from config import ParserReturn
import pytest


def test_parse_valid_config() -> None:
    """
    Test that a valid configuration file is parsed correctly.

    Validates that all required fields are present and have correct types.
    """
    parser: ParserReturn = ParserReturn("config.txt")
    result: Dict[str, Any] = parser.parse_config()
    assert isinstance(result["WIDTH"], int)
    assert isinstance(result["HEIGHT"], int)
    assert isinstance(result["ENTRY"], tuple)
    assert isinstance(result["EXIT"], tuple)
    assert isinstance(result["OUTPUT_FILE"], str)
    assert isinstance(result["PERFECT"], bool)
    assert len(result["ENTRY"]) == 2
    assert len(result["EXIT"]) == 2
    assert all(isinstance(coord, int) for coord in result["ENTRY"])
    assert all(isinstance(coord, int) for coord in result["EXIT"])


def test_missing_width() -> None:
    """Test that missing WIDTH field raises ValueError."""
    parser: ParserReturn = ParserReturn("tests/configs/missing_width.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_missing_height() -> None:
    """Test that missing HEIGHT field raises ValueError."""
    parser: ParserReturn = ParserReturn("tests/configs/missing_height.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_missing_entry() -> None:
    """Test that missing ENTRY field raises ValueError."""
    parser: ParserReturn = ParserReturn("tests/configs/missing_entry.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_missing_exit() -> None:
    """Test that missing EXIT field raises ValueError."""
    parser: ParserReturn = ParserReturn("tests/configs/missing_exit.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_missing_output_file() -> None:
    """Test that missing OUTPUT_FILE field raises ValueError."""
    parser: ParserReturn = ParserReturn(
        "tests/configs/missing_output_file.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_missing_perfect() -> None:
    """Test that missing PERFECT field raises ValueError."""
    parser: ParserReturn = ParserReturn("tests/configs/missing_perfect.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_invalid_width_not_integer() -> None:
    """Test that non-integer WIDTH raises ValueError."""
    parser: ParserReturn = ParserReturn(
        "tests/configs/invalid_width_string.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_invalid_width_out_of_range() -> None:
    """Test that WIDTH outside range 4-1024 raises ValueError."""
    parser: ParserReturn = ParserReturn(
        "tests/configs/invalid_width_range.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_invalid_height_not_integer() -> None:
    """Test that non-integer HEIGHT raises ValueError."""
    parser: ParserReturn = ParserReturn(
        "tests/configs/invalid_height_string.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_invalid_height_out_of_range() -> None:
    """Test that HEIGHT outside range 4-1024 raises ValueError."""
    parser: ParserReturn = ParserReturn(
        "tests/configs/invalid_height_range.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_invalid_entry_format() -> None:
    """Test that invalid ENTRY format raises ValueError."""
    parser: ParserReturn = ParserReturn(
        "tests/configs/invalid_entry_format.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_invalid_exit_format() -> None:
    """Test that invalid EXIT format raises ValueError."""
    parser: ParserReturn = ParserReturn(
        "tests/configs/invalid_exit_format.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_invalid_perfect_value() -> None:
    """Test that invalid PERFECT value raises ValueError."""
    parser: ParserReturn = ParserReturn("tests/configs/invalid_perfect.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_empty_output_file() -> None:
    """Test that empty OUTPUT_FILE raises ValueError."""
    parser: ParserReturn = ParserReturn("tests/configs/empty_output_file.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_entry_equals_exit() -> None:
    """Test that identical ENTRY and EXIT raises ValueError."""
    parser: ParserReturn = ParserReturn("tests/configs/entry_equals_exit.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_entry_out_of_bounds() -> None:
    """Test that ENTRY outside maze bounds raises ValueError."""
    parser: ParserReturn = ParserReturn(
        "tests/configs/entry_out_of_bounds.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_exit_out_of_bounds() -> None:
    """Test that EXIT outside maze bounds raises ValueError."""
    parser: ParserReturn = ParserReturn("tests/configs/exit_out_of_bounds.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_duplicate_keys() -> None:
    """Test that duplicate keys in config raise ValueError."""
    parser: ParserReturn = ParserReturn("tests/configs/duplicate_keys.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_invalid_line_format() -> None:
    """Test that line without '=' raises ValueError."""
    parser: ParserReturn = ParserReturn(
        "tests/configs/invalid_line_format.txt")
    with pytest.raises(ValueError):
        parser.parse_config()


def test_comments_and_empty_lines() -> None:
    """Test that comments and empty lines are properly ignored."""
    parser: ParserReturn = ParserReturn("tests/configs/with_comments.txt")
    result: Dict[str, Any] = parser.parse_config()
    assert isinstance(result["WIDTH"], int)
    assert isinstance(result["HEIGHT"], int)


def test_maze_too_small_for_42_pattern(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test that small maze prints warning but doesn't fail."""
    parser: ParserReturn = ParserReturn("tests/configs/small_maze.txt")
    result: Dict[str, Any] = parser.parse_config()
    captured = capsys.readouterr()
    assert "Warning" in captured.out
    assert isinstance(result, dict)
