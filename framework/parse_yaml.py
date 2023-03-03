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

# def run_without_database(endpoints_dict:dict):

#     routes = []
#     for view, specs in endpoints_dict.items():
#         url = specs['url']
#         return_text = specs['text']

#         json_response = {'text':return_text}
                        
#         routes.append(Route(url, endpoint=lambda x:JSONResponse(json_response))) 
                            
#     app = Starlette(routes=routes)     

#     return app                   
                            

def create_routes_list(apis, database: Database, models) -> list:
    app_routes = []


    for api in apis:
        db_table = apis['table']
        method = apis['methods']

        async def endpoint(request):
            query = await get_query(request, method, table)

            results = await get_execute_function(method, query, database)

            response = set_response(method, results)

            return response

        url =  '/' + str(db_table)
        table = import_from_models_file(models=models, module=db_table)

        app_routes.append(Route(url, endpoint=endpoint,methods=[method]))

    return app_routes      


# def create_view_function(database, method, table) -> callable:

#     async def view_function(request:Request) -> callable:

#         query = await get_query(request, method=method, table=table)

#         results = await get_execute_function(method=method, query=query, database=database)

#         return set_response(method=method, results=results)

#     return view_function 


async def get_query(request: Request, method: str, table):
    match method:
        case 'GET':
            return table.select()
        case 'POST':
            data = await request.json()
            return table.insert().values(data)


def get_execute_function(method: str, query, database: Database):
    match method:
        case 'GET':
            return database.fetch_all(query)
        case 'POST':
            return database.execute(query)


def set_response(method: str, results) -> JSONResponse:

    fields = ['title', 'url']

    match method:
        case 'GET':
            content = [
            {
                field: result[field] for field in fields
            }
            for result in results
            ]
            return JSONResponse(content)
        case 'POST':
            return JSONResponse({'OK':'OK'})
        


def import_from_models_file(models:str, module:str) -> Database:

    file_path = os.path.abspath(models)
    modulename = importlib.machinery.SourceFileLoader(models.removesuffix('.py'), file_path).load_module()

    return getattr(modulename, module)

