import importlib
import json
import common.utils as utils

def read_config(config_type : str):

    with open('..\\config\\config_' + config_type + '.json', encoding='UTF-8') as f_in:
        return json.load(f_in)

def write_config(config_type : str, config : object):

    with open('..\\config\\config_' + config_type + '.json', 'w', encoding='UTF-8') as f_out:
        json.dump(config, f_out, indent=4)

    return

def main():

    runs = read_config('runs')
    sources = read_config('sources')

    utils.log_start()

    for source_name in sources['data'].keys():
        source_data = sources['data'][source_name]
        runs_data = runs[sources['data'][source_name]['handler']]
        if (source_data['run']):
            handler_mod = importlib.import_module('handlers.handler_' + source_data['handler'])
            exec_verb_func = getattr(handler_mod, 'exec_verb')

            result, filename, filedatetime, new_run_id = exec_verb_func(source_data, runs_data['last_run_id'])

            utils.print_log(result)

            if (result):
                runs[source_data['handler']]['last_run_id'] = new_run_id
                write_config('runs', runs)
                converter_mod_name = 'converter_' + source_data['artifact_converter']
                converter_mod = importlib.import_module('converters.' + converter_mod_name)
                exec_verb_func = getattr(converter_mod, 'exec_verb')

                result = exec_verb_func(sources['options'][converter_mod_name], filename, filedatetime)

    return




if __name__=="__main__":

    main()
