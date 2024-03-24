from __future__ import annotations

from pathlib import Path
from typing import Tuple

CURRENT_FILE = Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parent.parent.parent
LOG_FILE = BASE_DIR / "app.log"
SETTINGS_FILE = BASE_DIR / "settings.json"


def checks_string_is_dir(value: str) -> Tuple[bool, str]:
    """Checks that a string represents a valid folder path"""
    
    path = Path(value)
    return (True, str(path)) if Path(path).is_dir() else (False, "")


def checks_string_is_int_between_limits(value: [str | int], mini: int, maxi: int) -> Tuple[bool, int]:
    """Checks that a string represents an integer between the limits passed"""

    if isinstance(value, int):
        value = str(value)

    if value.isdigit() and mini <= int(value) <= maxi:
        return True, int(value)
    return False, 0


def checks_string_is_list_of_int_between_limits(value: [str | list], mini: int, maxi: int) -> Tuple[bool, list]:
    """Checks that a string represents a list of integers between the limits passed"""

    if isinstance(value, list):
        value = ",".join(str(v) for v in value)

    tests = [
        checks_string_is_int_between_limits(v, mini, maxi)
        for v in value.replace(" ", "").split(",")
    ]
    if all(test[0] for test in tests):
        return True, [test[1] for test in tests]
    return False, []


def checks_string_matches_boolean_choice(value: [str | bool]) -> Tuple[bool, bool]:
    """Checks that a character string corresponds to a Boolean choice"""

    if isinstance(value, bool):
        return True, value

    value = value.lower()
    if value in {"o", "y", "oui", "yes"}:
        return True, True
    elif value in {"n", "no", "non"}:
        return True, False
    return False, False
