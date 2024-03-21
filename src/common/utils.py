import logging
import sys
import json
from typing import Any

def log_start(options: dict):

    handlers = [
        logging.StreamHandler(stream=sys.stdout),
        logging.FileHandler(filename=options['output'])
    ]
    logging.basicConfig(level=logging.getLevelName(options['level']), style=options['style'], format=options['format'], handlers=handlers)
    log_print('logging started')

def log_end():

    log_print('logging ended')
    logging.shutdown()

def log_print(inputval : Any) -> None:

    try:
        finalval = json.dumps(inputval)
    except TypeError:
        finalval = str(inputval)
    logging.log(level=logging.getLogger().level, msg=finalval)
