import importlib
import json

def read_config(config_type : str):

    with open('..\\config\\config_' + config_type + '.json', encoding='UTF-8') as f_in:
        return json.load(f_in)

sources = read_config('sources')

def main():

    for source_name in sources['data'].keys():
        source_data = sources['data'][source_name]
        if (source_data['run']):

            handler_mod = importlib.import_module('handlers.handler_' + source_data['handler'])
            exec_verb_func = getattr(handler_mod, 'exec_verb')

            result, filename, filedatetime = exec_verb_func(source_data)
            print(result)
            if (result):
                converter_mod = importlib.import_module('converters.converter_' + source_data['converter'])
                exec_verb_func = getattr(converter_mod, 'exec_verb')

                result = exec_verb_func(source_data, filename, filedatetime)

    return




if __name__=="__main__":

    main()
