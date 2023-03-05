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
from .utils import import_from_file
from .requests import get_request, post_request, put_request, delete_request


def create_app_from_config(config:dict)-> Starlette:

    database_name = config.get('database')
    models = config.get('models')
    apis = config.get('apis')

    database = import_from_file(file_name=models, object=database_name)

    app_routes = create_routes_list(apis, database, models)


        
    app =  Starlette(
                routes=app_routes,
                on_startup=[database.connect],
                on_shutdown=[database.disconnect]
            )

    return app    
          

def create_routes_list(apis, database: Database, models) -> list:
    app_routes = []

    for api in apis:
        db_table = apis['table']
        url =  '/' + str(db_table)
        table = import_from_file(file_name=models, object=db_table)
        methods = list(apis['methods'])


        for method in methods:
            endpoint = create_view_function(method, database, table)
            app_routes.append(Route(url, endpoint=endpoint,methods=[method]))

    return app_routes     




def create_view_function(method, database, table):

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
