import importlib
import importlib.machinery
from pathlib import Path
import os

import yaml
from databases import Database
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .queries import raw_queries
from .responses import responses
from .utils import import_from_file, get_key_from_config, import_all_database_tables
from .requests import get_request, post_request, put_request, delete_request



database_name = get_key_from_config('database')
models_file = get_key_from_config('models')
apis = get_key_from_config('apis')

database = import_from_file(file_name=models_file, object=database_name)
database_tables = import_all_database_tables(apis, models_file)



def create_app_from_config(config:dict)-> Starlette:

    all_routes = []

    for name, specs in apis.items():
        
        table_name = specs['table']
        url =  '/' + str(table_name)
        methods = specs['methods']
        routes = [create_route(method=method, url=url, table_name=table_name) for method in methods]

        all_routes.extend(routes)
        
    app =  Starlette(
                routes=all_routes,
                on_startup=[database.connect],
                on_shutdown=[database.disconnect]
            )

    return app    



def create_route(method, url, table_name):
    endpoint = create_view_function(method, table_name)
    route = Route(url, endpoint=endpoint,methods=[method])
    return route



def create_view_function(method, table_name):

    table = database_tables[table_name]

    async def create_function(request):
        match method:
            case 'GET':
                return await get_request(request, database, table)
            case 'POST':
                return await post_request(request, database, table)
            case 'PUT':
                return await put_request(request, database, table)
            case 'DELETE':
                return await delete_request(request, database, table)
            
    return create_function        


