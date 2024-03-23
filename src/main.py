import importlib
import json
import argparse
import common.utils as utils

CONFIG_FILE_BASE_DEFAULT  = '..\\config\\config_'
SOURCES_TODO_DEFAULT = '*'
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--configbase', help=f'base location/prefix of config files (default = "{CONFIG_FILE_BASE_DEFAULT}")', default=CONFIG_FILE_BASE_DEFAULT)
arg_parser.add_argument('--sources', help=f'comma-sep list of sources to load (default = "{SOURCES_TODO_DEFAULT}")', default=SOURCES_TODO_DEFAULT)
args = arg_parser.parse_args()

def config_read(config_type : str, log = True):

    config_file = args.configbase + config_type + '.json'
    with open(config_file, 'r', encoding='UTF-8') as f_in:
        if (log):
            utils.log_print(f"reading config file = {config_file}")
        return json.load(f_in)

def config_write(config_type : str, config : object):

    config_file = args.configbase + config_type + '.json'
    with open(config_file, 'w', encoding='UTF-8') as f_out:
        utils.log_print(f"writing config file = {config_file}")
        json.dump(config, f_out, indent=4)
    return

def process(sources_todo : str = SOURCES_TODO_DEFAULT, discard_new_run_id : bool = False) -> int:
    """
    this is the primary processor for collecting test data files from various CI pipelines
    it uses config files to specifiy which CI pipelines from which providers need
    to be queried, and it dynamically loads provider-specific handler modules to access
    the pipelines and download the artifacts. then it calls filetype-specific converters
    to convert the data files into a common CSV format, that can then be loaded into the
    DB or visualization product of choice

    Parameters:
    sources_todo (str): comma-separated list of sources to process
    discard_new_run_id (bool): do not write the new run id to the config file (for testing)
    """

#   open all config files and start logging
    options = config_read('options', False)
    utils.log_start(options['logging'])
    sources = config_read('sources')
    runs = config_read('runs')
    sources_todo_list = sources_todo.split(',')

#   iterate through all the sources and see if any of them are specified for execution
    for source_name in sources['data']:
        if ((sources_todo_list == [SOURCES_TODO_DEFAULT]) or (source_name in sources_todo_list)):
            utils.log_print(f"processing source = {source_name} from config_sources file")

#   load the data for that source and its run data
            source_data = sources['data'][source_name]
            run_data = runs[source_name]
            utils.log_print(f"source = {source_name} has run = {str(source_data['run'])}")
            utils.log_print(f"source = {source_name} has last_run_id = {str(run_data['last_run_id'])}")

#   if the source is enabled
            if (source_data['run']):
                utils.log_print(f"source = {source_name} has handler = {source_data['handler']}")
                handler_mod_name = 'handlers.handler_' + source_data['handler']

#   load its handler and execute it
                handler_mod = importlib.import_module(handler_mod_name)
                exec_verb_func = getattr(handler_mod, 'exec_verb')
                utils.log_print(f"calling handler = {handler_mod_name}")
                result_handler, filename, filedatetime, new_run_id = exec_verb_func(source_data, run_data['last_run_id'])
                utils.log_print(f"result from handler = {str(result_handler)}")

#   if we got a file back, then run the converter against that file
                if (result_handler):
                    converter_name = source_data['artifact_converter']
                    utils.log_print(f"source = {source_name} has converter = {converter_name}")
                    converter_mod_name = 'converters.converter_' + converter_name
                    converter_mod = importlib.import_module(converter_mod_name)
                    exec_verb_func = getattr(converter_mod, 'exec_verb')
                    utils.log_print(f"calling converter = {converter_mod_name}")
                    result_converter = exec_verb_func(options['converters'][converter_name], filename, filedatetime)
                    utils.log_print(f"result from converter = {str(result_converter)}")

#   if the converter worked, then optionally update the run data
                    if (result_converter):
                        utils.log_print(f"new run id = {str(new_run_id)} for handler {handler_mod_name}")
                        if (not discard_new_run_id):
                            run_data['last_run_id'] = new_run_id
                            config_write('runs', runs)
                            utils.log_print(f"updated config_runs file with new run id")

    utils.log_end()

    return new_run_id

if __name__=="__main__":

    process(args.sources)
