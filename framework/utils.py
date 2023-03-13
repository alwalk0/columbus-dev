import importlib
import importlib.machinery
import os
from starlette.routing import Route
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
import yaml
from columbus.startup_script import MAIN_CONFIG_NAME


def import_from_file(file_name: str, object: str) -> any:
    if not os.path.exists(file_name):
        raise Exception('No such file: {}'.format(file_name))
    file_path = os.path.abspath(file_name)
    modulename = importlib.machinery.SourceFileLoader(
        file_name.removesuffix(".py"), file_path
    ).load_module()
    if not hasattr(modulename, object):
        raise Exception('No object {} in file {}.'.format(object, file_name))
    return getattr(modulename, object)


def import_all_database_tables(apis: str, models_file: str) -> dict:
    table_names = [v["table"] for k, v in apis.items()]
    imported_tables = [
        import_from_file(file_name=models_file, object=table) for table in table_names
    ]
    tables_dict = {table.name: table for table in imported_tables}
    return tables_dict


def do_database_setup():
    with open(MAIN_CONFIG_NAME, "r") as file:
        config_dict = yaml.safe_load(file)

    database_name = config_dict["database"]
    models_file = config_dict["models"]
    apis = config_dict["apis"]

    database = import_from_file(models_file, database_name)
    database_tables = import_all_database_tables(apis, models_file)
    return database, database_tables


def run_without_database() -> Starlette:
    welcome = "Welcome to Columbus. Please set up the database to generate APIs."

    routes = [Route("/", endpoint=lambda request: PlainTextResponse(welcome))]
    app = Starlette(routes=routes)

    return app
