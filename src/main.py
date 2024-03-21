import importlib
import json
import argparse
import common.utils as utils

arg_parser = argparse.ArgumentParser()
CONFIG_FILE_BASE_DEFAULT  = '..\\config\\config_'
arg_parser.add_argument('--configbase', help=f'base location/prefix of config files (default = "{CONFIG_FILE_BASE_DEFAULT}")', default=CONFIG_FILE_BASE_DEFAULT)
args = arg_parser.parse_args()

def config_read(config_type : str, log = True):

    config_file = args.configbase + config_type + '.json'
    with open(config_file, 'r', encoding='UTF-8') as f_in:
        if (log):
            utils.log_print("reading config file: " + config_file)
        return json.load(f_in)

def config_write(config_type : str, config : object):

    config_file = args.configbase + config_type + '.json'
    with open(config_file, 'w', encoding='UTF-8') as f_out:
        utils.log_print("writing config file: " + config_file)
        json.dump(config, f_out, indent=4)
    return

def main():
    """
    this is the main processor for collecting test data files from various CI pipelines
    it uses config files to specifiy which CI pipelines from which providers need
    to be queried, and it dynamically loads provider-specific handler modules to access
    the pipelines and download the artifacts. then it calls filetype-specific converters
    to convert the data files into a common CSV format, that can then be loaded into the
    DB or visualization product of choice

    """

    options = config_read('options', False)
    utils.log_start(options['logging'])
    sources = config_read('sources')
    runs = config_read('runs')

    for source_name in sources['data']:
        utils.log_print("processing source: " + source_name)
        source_data = sources['data'][source_name]
        run_data = runs[source_name]
        utils.log_print("source: " + source_name + " has run = " + str(source_data['run']))
        utils.log_print("source: " + source_name + " has last_run_id = " + str(run_data['last_run_id']))

        if (source_data['run']):
            utils.log_print("source: " + source_name + " has handler = " + source_data['handler'])
            handler_mod_name = 'handlers.handler_' + source_data['handler']
            handler_mod = importlib.import_module(handler_mod_name)
            exec_verb_func = getattr(handler_mod, 'exec_verb')

            utils.log_print("calling handler: " + handler_mod_name)
            result_handler, filename, filedatetime, new_run_id = exec_verb_func(source_data, run_data['last_run_id'])
            utils.log_print("result from handler = " + str(result_handler))
            if (result_handler):
                converter_name = source_data['artifact_converter']
                utils.log_print("source: " + source_name + " has converter = " + converter_name)
                converter_mod_name = 'converters.converter_' + converter_name
                converter_mod = importlib.import_module(converter_mod_name)
                exec_verb_func = getattr(converter_mod, 'exec_verb')

                utils.log_print("calling converter: " + converter_mod_name)
                result_converter = exec_verb_func(options['converters'][converter_name], filename, filedatetime)
                utils.log_print("result from converter = " + str(result_converter))
                if (result_converter):
                    run_data['last_run_id'] = new_run_id
                    config_write('runs', runs)
                    utils.log_print("new run id = " + str(new_run_id) + " for handler: " + handler_mod_name)

    utils.log_end()

    return


if __name__=="__main__":

    main()
