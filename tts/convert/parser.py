import contextlib
import logging
from datetime import datetime
from pathlib import Path
from re import compile
from typing import Tuple

from tts.settings.config import get_path_output_tricarb

PARAM_PROTOCOL = ("P#", "DATE", "TIME", "COUNTFILE", "PROTNAME", "CTIME",
                  "LLA", "ULA", "LLB", "ULB", "LLC", "ULC", "#/VIAL", "#/SMPL")

PATTERN_HEADERS = r"(?=.*P#)(?=.*S#)(?=.*Count Time)(?=.*CPMA)(?=.*CPMB)(?=.*CPMC)(?=.*tSIE)(?=.*DATE)(?=.*TIME).*"

PATTERNS = {
    "P#": r"\d*",
    "S#": r"\d*",
    "Count Time": r"\d+\.?\d*",
    "CPMA": r"\d+\.?\d*",
    "CPMB": r"\d+\.?\d*",
    "CPMC": r"\d+\.?\d*",
    "tSIE": r"\d+\.?\d*",
    "other": r".*"
}


def _get_protocol_setting(path: Path) -> dict:
    protocol_path = path / "prot.dat"
    return dict([line.split('=') for line in protocol_path.read_text().splitlines()[:-1]])


def _get_report(path: Path, file: str) -> list:
    report_path = path / file
    return report_path.read_text().splitlines()


def _find_headers(report: list) -> Tuple[str, int]:
    headers, num_row = '', 0
    for num_row, row in enumerate(report):
        if compile(PATTERN_HEADERS).findall(row):
            headers = row
            break
    return headers, num_row


def _determine_splitter(splitted_string: str) -> str:
    return (
        splitted_string[i - 1]
        if (i := splitted_string.index("S#"))
        else splitted_string[splitted_string.index("P#") - 1]
    )


def _build_pattern_counts(headers: str, splitter: str) -> str:
    return ''.join(PATTERNS.get(header, PATTERNS['other']) + ","
                   for header in headers.split(splitter))[:-1]


def _replace_separators(string: str, splitter: str) -> str:
    return ",".join(el.replace(",", ".") for el in string.split(splitter))


def _find_counts(headers: str, splitter: str, report: list, start_row: int):
    pattern = _build_pattern_counts(headers, splitter)

    counts = []
    for row in report[start_row:]:
        row = _replace_separators(row, splitter)
        if compile(pattern).findall(row):
            counts.append(row)

    return counts


def _parse_text_datetime(text: str) -> datetime:
    for fmt in {"%d/%m/%Y %H:%M:%S", "%m/%d/%Y %I:%M:%S %p"}:
        with contextlib.suppress(ValueError):
            return datetime.strptime(text, fmt)
    logging.error("Date et heure d'une ligne de résultat n'est pas reconnue.")
    raise ValueError("Date et heure d'une ligne de résultat n'est pas reconnue.")


def _parse_date_time(headers: str, counts: list) -> list:
    headers = headers.split(",")
    counts_datetime = []
    for count in counts:
        count_datetime = count.split(",")
        date_time = _parse_text_datetime(
            f"{count_datetime[headers.index('DATE')]} {count_datetime[headers.index('TIME')]}")
        count_datetime[headers.index('DATE')] = date_time.strftime("%d/%m/%Y")
        count_datetime[headers.index('TIME')] = date_time.strftime("%H%M")
        counts_datetime.append(",".join(count_datetime))
    return counts_datetime


def parser() -> dict:
    output_path = get_path_output_tricarb()
    protocol_setting = _get_protocol_setting(output_path)
    report_counts = _get_report(output_path, protocol_setting.get("COUNTFILE", ""))
    headers_counts, num_row_headers = _find_headers(report_counts)
    splitter = _determine_splitter(headers_counts)
    counts = _find_counts(headers_counts, splitter, report_counts, num_row_headers + 1)
    headers_counts = _replace_separators(headers_counts, splitter)
    counts = _parse_date_time(headers_counts, counts)
    return {
        "headers": headers_counts,
        "protocol_setting": protocol_setting,
        "counts": counts
    }
