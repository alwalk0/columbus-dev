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

    fields = [column.key for column in table.columns]

    if request.query_params:
        query = "SELECT * FROM articles WHERE id = :id"
        #todo: return if doesnt exist
        result = await database.fetch_one(query=query, values={"id": int(request.query_params['id'])})
        content = {
            field: result[field] for field in fields
        }          
        response =  JSONResponse(content)       

    else:           

        query = table.select()
        results = await database.fetch_all(query)
        content = [
        {
            field: result[field] for field in fields
        }
        for result in results
        ]
        response =  JSONResponse(content)

    return response    


async def post_request(request, database, table):
    data = await request.json()
    query = table.insert().values(data)
    await database.execute(query)
    return JSONResponse({'ok': 'ok'})


async def put_request(request, database, table):
    fields = [column.key for column in table.columns if column.key != 'id']
    fields_string = [f'{field} = :{field}'.format(field) for field in fields]
    print(fields_string)
    data = await request.json()
    #todo: check if exists
    if request.query_params:
        query = "UPDATE articles SET {} WHERE id = :id".format(', '.join(fields_string))
        print(query)
        
        result = await database.execute(query=query, values={"id": int(request.query_params['id']), 'title': 'hello'})
        return JSONResponse({'ok': 'ok'})


async def delete_request(request, database, table):
    #todo: check if exists
    query = "DELETE FROM articles WHERE id = :id"
    result = await database.execute(query=query, values={"id": int(request.query_params['id'])})
    return JSONResponse({'ok': 'ok'})




def import_from_models_file(models:str, module:str) -> Database:

    file_path = os.path.abspath(models)
    modulename = importlib.machinery.SourceFileLoader(models.removesuffix('.py'), file_path).load_module()

    return getattr(modulename, module)

