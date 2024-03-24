from json import load, dump
from pathlib import Path
from typing import Any, Tuple

from settings.utils import SETTINGS_FILE, checks_string_is_int_between_limits, checks_string_is_dir, \
    checks_string_is_list_of_int_between_limits, checks_string_matches_boolean_choice

SETTINGS = {
    "code_tricarb": {"default": 0,
                     "question": "Numéro SIRENe de l'instrument => ",
                     "expected_type": "number",
                     "limit_min": 1,
                     "limit_max": 20},
    "dir_output_data": {"default": "",
                        "question": "Chemin du dossier des résultats brutes du TriCarb => ",
                        "expected_type": "dir"},
    "dir_src_PAS": {"default": "",
                    "question": "Chemin du dossier surveillé par PAS => ",
                    "expected_type": "dir"},
    "protocol_maintenance": {"default": [],
                             "question": "Numéros des protocoles maintenances (séparés par une virgule) => ",
                             "expected_type": "list_number",
                             "limit_min": 1,
                             "limit_max": 60},
    "extension_maintenance": {"default": 0,
                              "question": "Numéro de la dernière trame maintenance générée (0 si première) => ",
                              "expected_type": "number",
                              "limit_min": 0,
                              "limit_max": 999},
    "extension_analysis": {"default": 0,
                           "question": "Numéro de la dernière trame analyse générée (0 si première) => ",
                           "expected_type": "number",
                           "limit_min": 0,
                           "limit_max": 999},
    "print_by_application": {"default": "",
                             "question": "Impression en local géré par l'application (O/N) => ",
                             "expected_type": "boolean_choice"},
    "print_independent_protocol": {"default": "",
                                   "question": "Impression multiple pour les protocoles indépendants (O/N) => ",
                                   "expected_type": "boolean_choice"}
}


def _get_settings() -> dict:
    """Returns parameters in dictionary format"""

    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return load(f)


def set_settings(settings: dict) -> None:
    """Saves settings in dictionary format in the settings.json file"""

    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        dump(settings, f, indent=4, ensure_ascii=False)


def settings_file_exists() -> bool:
    """Returns True if the settings file exists, otherwise False"""

    return SETTINGS_FILE.exists()


def init_settings() -> None:
    """Reset to default settings"""

    set_settings(SETTINGS_FILE)


def _check_parameter(answer: str, question: dict) -> Tuple[bool, Any]:
    """Checks that the answer to a question is valid"""

    expected = question.get("expected_type")
    if expected == "number":
        return checks_string_is_int_between_limits(answer, question["limit_min"], question["limit_max"])
    elif expected == "dir":
        return checks_string_is_dir(answer)
    elif expected == "list_number":
        return checks_string_is_list_of_int_between_limits(answer, question["limit_min"], question["limit_max"])
    elif expected == "boolean_choice":
        return checks_string_matches_boolean_choice(answer)
    return False, False


def settings_is_valid() -> bool:
    """Checks that the settings file is valid"""

    for setting, value in _get_settings().items():
        test, v = _check_parameter(value, SETTINGS[setting])
        if not test:
            return False
    return True


def determine_parameters() -> dict:
    """Queries the user to determine the settings"""

    settings, value = {}, 0
    for parameter, config in SETTINGS.items():
        test = False
        while not test:
            test, value = _check_parameter(input(config.get("question")), config)
        settings[parameter] = value
    return settings


def get_path_output_tricarb() -> Path:
    """Returns the path to the QuantaSmart raw results output folder"""

    return Path(_get_settings()["dir_output_data"])


def get_path_src_PAS() -> Path:
    """Returns the path of the folder monitored by the PAS application"""

    return Path(_get_settings()["dir_src_PAS"])


def set_settings_extension(type_protocol: str, extension: int) -> None:
    """Registers the extension for the type of protocol passed in the settings file"""

    settings = _get_settings()
    settings[type_protocol] = extension
    set_settings(settings)


def get_next_extension(type_protocol: str) -> str:
    """Returns the next extension for the given protocol type"""

    extension = _get_settings()[type_protocol]
    extension = extension + 1 if extension < 999 else 1
    set_settings_extension(type_protocol, extension)
    return str(extension).zfill(3)


def get_code_tricarb() -> int:
    """Returns the number assigned to the TriCarb"""

    return _get_settings()["code_tricarb"]


def get_list_protocols_maintenance() -> tuple:
    """Returns the list of maintenance protocols"""

    return tuple(_get_settings()["protocol_maintenance"])


def get_feature_print_is_enabled(feature: str) -> bool:
    """Returns whether the print functionality passed in parameter is activated"""

    return _get_settings()[feature]
