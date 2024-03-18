import logging
import datetime
import json
from typing import Any

def _datetime_format() -> str:

    return "{logtimestamp:%Y-%m-%dT%H:%M:%S} ".format( logtimestamp=datetime.datetime.now())

def log_start():

    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    print_log('Started')

def print_log(inputval : Any) -> None:

    final = ''

    try:
        final = json.dumps(inputval)
    except TypeError:
        final = str(inputval)
    log_entry = _datetime_format() + final

    print(log_entry)
    logging.info(log_entry)
