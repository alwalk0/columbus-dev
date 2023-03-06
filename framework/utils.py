import importlib
import importlib.machinery
from pathlib import Path
import os
import yaml


def import_from_file(file_name:str, object:str) -> any:
    file_path = os.path.abspath(file_name)
    modulename = importlib.machinery.SourceFileLoader(file_name.removesuffix('.py'), file_path).load_module()

    return getattr(modulename, object)



def get_key_from_config(key_name:str)->str:
    file_path = os.path.abspath('main.yml')
    with open(file_path, 'r') as file:
        config_dict = yaml.safe_load(file)
        return config_dict[key_name]



def import_all_database_tables(apis:str, models_file:str) ->dict:
    table_names = [v['table'] for k,v in apis.items()]   
    imported_tables = [import_from_file(file_name=models_file, object=table) for table in table_names]
    tables_dict = {table.name: table for table in imported_tables}
    return tables_dict

