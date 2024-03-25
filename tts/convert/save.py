from datetime import datetime
from os import startfile
from pathlib import Path

import tts.settings.config as cf


def _get_type_of_frame(number_protocol: str):
    return ("M", "extension_maintenance"
            if cf.number_protocol_is_maintenance(int(number_protocol))
            else "A", "extension_analysis")


def _make_path_rtf_file(txt_file: str) -> Path:
    return Path(cf.get_path_output_tricarb()) / txt_file.replace(".txt", ".rtf")


def main_save(frames: list, protocol_setting: dict):
    type_frame = _get_type_of_frame(protocol_setting["P#"])
    rtf_file = _make_path_rtf_file(protocol_setting["COUNTFILE"])
    for i, frame in enumerate(frames):
        frame_list = frame.split(',')
        extension = cf.get_next_extension(type_frame[1])
        filename = f"{type_frame[0]}{frame_list[0]}{datetime.now().strftime('%d%m%y')}.{extension}"
        with open(Path(cf.get_path_src_PAS()) / filename, 'w', encoding="utf-8") as f:
            f.write(frame)
        if i and cf.get_feature_print_is_enabled("print_independent_protocol"):
            startfile(rtf_file, "print")
    if cf.get_feature_print_is_enabled("print_by_application"):
        startfile(rtf_file, "print")
