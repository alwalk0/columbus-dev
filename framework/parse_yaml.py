import importlib
import importlib.machinery
from pathlib import Path
import inspect
import os

import yaml
from databases import Database
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .queries import raw_queries
from .responses import responses


def create_app_from_config(config:dict)-> Starlette:

    database_name = config.get('database')
    models = config.get('models')
    apis = config.get('apis')

    database = import_from_models_file(models, database_name)

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
        table = import_from_models_file(models=models, module=db_table)
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


async def get_request(request, database, table):

    if request.query_params:
        query = raw_queries['get_one'](table)
        #todo: return if doesnt exist
        result = await database.fetch_one(query=query, values={"id": int(request.query_params['id'])})     
        response =  JSONResponse(responses['GET_one'](table, result))       

    else:           

        query = table.select()
        results = await database.fetch_all(query)
        response =  JSONResponse(responses['GET_all'](table, results))

    return response    


async def post_request(request, database, table):
    data = await request.json()
    query = table.insert().values(data)
    await database.execute(query)
    return JSONResponse(responses['POST'])


async def put_request(request, database, table):
    data = await request.json()
    if request.query_params:
        query = raw_queries['PUT'](table)
        result = await database.execute(query=query, values={"id": int(request.query_params['id']), 'title': 'hello'})
        return JSONResponse(responses['PUT'])


async def delete_request(request, database, table):
    if request.query_params:
        query = raw_queries['DELETE'](table)
        result = await database.execute(query=query, values={"id": int(request.query_params['id'])})
        return JSONResponse(responses['DELETE'])




def import_from_models_file(models:str, module:str) -> Database:

    file_path = os.path.abspath(models)
    modulename = importlib.machinery.SourceFileLoader(models.removesuffix('.py'), file_path).load_module()

    return getattr(modulename, module)

