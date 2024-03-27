from datetime import datetime
from os import startfile
from pathlib import Path
from typing import Tuple

import tts.settings.config as cf


def _get_type_of_frame(number_protocol: str) -> Tuple[str, str]:
    return (("M", "extension_maintenance")
            if cf.number_protocol_is_maintenance(int(number_protocol))
            else ("A", "extension_analysis"))


def _make_path_rtf_file(txt_file: str) -> Path:
    return Path(cf.get_path_output_tricarb()) / txt_file.replace(".txt", ".rtf")


def _save_frames(frames: list, type_frame: Tuple[str, str], rtf_file: Path) -> None:
    multi_print = type_frame[0] == 'A' and cf.get_feature_print_is_enabled("print_independent_protocol")
    PAS_file = Path(cf.get_path_src_PAS())
    for i, frame in enumerate(frames):
        extension = cf.get_next_extension(type_frame[1])
        filename = f"{type_frame[0]}{frame.split(',')[0]}{datetime.now().strftime('%d%m%y')}.{extension}"
        _send_to_PAS(PAS_file, filename, frame)
        if i and multi_print:
            _print_file(rtf_file)


def _send_to_PAS(path: Path, filename: str, frame: str) -> None:
    with open(path / filename, 'w', encoding="utf-8") as f:
        f.write(frame)


def _print_file(file: Path) -> None:
    startfile(file, "print")


def save(frames: list, protocol_setting: dict):
    type_frame = _get_type_of_frame(protocol_setting["P#"])
    rtf_file = _make_path_rtf_file(protocol_setting["COUNTFILE"])
    _save_frames(frames, type_frame, rtf_file)
    if cf.get_feature_print_is_enabled("print_by_application"):
        _print_file(rtf_file)
