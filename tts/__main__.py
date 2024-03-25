import logging
import sys

from tts.convert.builder import builder
from tts.convert.parser import parser
from tts.convert.save import save
from tts.settings.config import check_settings, determine_parameters
from tts.settings.utils import LOG_FILE


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        filename=LOG_FILE,
        filemode='a',
        format='%(levelname)s - %(asctime)s : %(message)s'
    )


def main(option: str):
    configure_logging()

    if option == "config":
        determine_parameters()
        sys.exit()

    if check_settings():
        result_parsed = parser()
        frames = builder(result_parsed)
        save(frames, result_parsed["protocol_setting"])


if __name__ == '__main__':
    main(sys.argv[-1])
    # main("config")
