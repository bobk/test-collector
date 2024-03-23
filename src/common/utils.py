import logging
import os
import sys
import json
from typing import Any

FILE_ROOT_PATH = os.environ['TEST-COLLECTOR_FILE_ROOT_PATH']
OUTPUT_PATH = os.path.join(FILE_ROOT_PATH, 'output')

def trace(func):
    """
    function decorator to add common output for each decorated function call
    """

    def wrapper(*args, **kwargs):
        log_print(f"entering function = {func.__name__} in file = {func.__code__}")
        log_print(f"args = ({args!r}, {kwargs!r})")
        log_print(f"working dir = {os.getcwd()}")
        result = func(*args, **kwargs)
        log_print(f"result = {result!r}")
        return result
    return wrapper

def log_start(options: dict):
    """
    called once by main, to set up the logger with the options defined in the config file
    logs to file and to stdout
    """

    handlers = [
        logging.StreamHandler(stream=sys.stdout),
        logging.FileHandler(filename=options['output_file'])
    ]
    logging.basicConfig(level=logging.getLevelName(options['level']), style=options['style'], format=options['format'], handlers=handlers)
    log_print('logging started up')

def log_end():
    """
    called once by main to shutdown logging
    """

    log_print('logging shut down')
    logging.shutdown()

def log_print(inputval : Any) -> None:
    """
    called by all modules to log output
    if input is JSON-serializable, then dumps it out formatted
    """

    try:
        finalval = json.dumps(inputval)
    except TypeError:
        finalval = str(inputval)
    logging.log(level=logging.getLogger().level, msg=finalval)
