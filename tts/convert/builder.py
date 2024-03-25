from datetime import datetime as dt

import tts.settings.config as cf


def _make_base_of_frame(protocol_setting: dict) -> str:
    return f"{cf.get_code_tricarb()},{protocol_setting['P#']},"


def _protocol_is_independent(protocol_setting: dict) -> bool:
    return protocol_setting["PROTNAME"].endswith("_inde.lsa")


def _limit_channels(protocol_setting: dict) -> str:
    return ','.join(protocol_setting[item] for item in ('LLA', 'ULA', 'LLB', 'ULB', 'LLC', 'ULC'))


def _build_dependent_frame(base: str, protocol_setting: dict, counts: list, headers: str) -> list:
    sample = '0'
    frame = f"{base}{_date_format(protocol_setting['DATE'])},{protocol_setting['TIME'].replace(':', '')},"
    frame = f"{frame}{_limit_channels(protocol_setting)},{protocol_setting['CTIME']}"
    for count in counts:
        c = dict(zip(headers.split(","), count.split(",")))
        frame += ","
        if sample != c['S#']:
            sample = c['S#']
            frame += f"{sample},"
        frame += f"{c['CPMA']},{c['CPMB']},{c['CPMC']},{c['tSIE']}"
    return [frame]


def _build_independent_frame(base: str, protocol_setting: dict, counts: list, headers: str) -> list:
    raw_frames = {}
    for count in counts:
        c = dict(zip(headers.split(","), count.split(",")))
        if not raw_frames.get(c['S#']):
            raw_frames[c["S#"]] = []
        sub_frame = f"{base}{c['DATE']},{c['TIME']},{_limit_channels(protocol_setting)},{protocol_setting['CTIME']},"
        sub_frame += f"{c['S#']},{c['CPMA']},{c['CPMB']},{c['CPMC']},{c['tSIE']}"
        raw_frames[c['S#']].append(sub_frame)
    clean_frame, cleaned_frames = [], []
    for k in raw_frames:
        first = True
        for sub_frame in raw_frames[k]:
            if first:
                clean_frame = sub_frame.split(',')[:12]
                first = False
            clean_frame[2:4] = sub_frame.split(',')[2:4]
            clean_frame.extend(sub_frame.split(',')[12:])
        cleaned_frames.append(','.join(clean_frame))
    return cleaned_frames


def _date_format(date: str) -> str:
    return dt.strptime(date, "%d-%m-%y").strftime("%d/%m/%Y")


def main_builder(result_parsed: dict) -> list:
    base = _make_base_of_frame(result_parsed["protocol_setting"])
    return (
        _build_independent_frame(base, **result_parsed)
        if _protocol_is_independent(result_parsed["protocol_setting"])
        else _build_dependent_frame(base, **result_parsed)
    )
