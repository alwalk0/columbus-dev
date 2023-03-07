from sqlalchemy import Table

import yaml
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .queries import raw_queries
from .responses import responses
from .utils import import_from_file, import_all_database_tables

CONFIG_NAME = "main.yml"


with open(CONFIG_NAME, "r") as file:
    config_dict = yaml.safe_load(file)


database_name = config_dict["database"]
models_file = config_dict["models"]
apis = config_dict["apis"]

database = import_from_file(models_file, database_name)
database_tables = import_all_database_tables(apis, models_file)


def create_app() -> Starlette:
    specs_list = apis.values()

    routes = list(map(create_routes_list, specs_list))
    all_routes = sum(routes, [])

    app = Starlette(
        routes=all_routes,
        on_startup=[database.connect],
        on_shutdown=[database.disconnect],
    )

    return app


def create_routes_list(specs: dict) -> list:
    url = "/" + str(table_name)
    table_name = specs["table"]
    methods = specs["methods"]
    routes = [
        create_route(method=method, url=url, table_name=table_name)
        for method in methods
    ]
    routes.append(
        create_route(method="GET", url=url, table_name=table_name, no_arg=True)
    )

    return routes


def create_route(method: str, url: str, table_name: str, no_arg=False) -> Route:
    route_url = url if no_arg is True or method == "POST" else url + "/{id:int}"
    endpoint = create_view_function(method, table_name)
    route = Route(route_url, endpoint=endpoint, methods=[method])
    return route


def create_view_function(method: str, table_name: str):
    table = database_tables[table_name]

    async def create_function(request: Request):
        match method:
            case "GET":
                return await get_request(request, table)
            case "POST":
                return await post_request(request, table)
            case "PUT":
                return await put_request(request, table)
            case "DELETE":
                return await delete_request(request, table)

    return create_function


async def get_request(request: Request, table: Table) -> JSONResponse:
    if request.path_params:
        query = raw_queries["GET_one"](table)
        pk = request.path_params["id"]
        result = await database.fetch_one(query=query, values={"id": pk})
        response = responses["GET_one"](table, result)
        json_response = JSONResponse(response)
    else:
        query = table.select()
        results = await database.fetch_all(query)
        response = responses["GET_all"](table, results)
        json_response = JSONResponse(response)

    return json_response


async def post_request(request: Request, table: Table) -> JSONResponse:
    data = await request.json()
    query = table.insert().values(data)
    result = await database.execute(query)
    response = responses["POST"](result)
    return JSONResponse(response)


async def put_request(request: Request, table: Table) -> JSONResponse:
    data = await request.json()
    if request.query_params:
        query = raw_queries["PUT"](table)
        pk = int(request.query_params["id"])
        values = {"id": pk} | data
        result = await database.execute(query=query, values=values)
        response = responses["PUT"](pk)
        return JSONResponse(response)


async def delete_request(request: Request, table: Table) -> JSONResponse:
    if request.query_params:
        query = raw_queries["DELETE"](table)
        pk = int(request.query_params["id"])
        result = await database.execute(query=query, values={"id": pk})
        response = responses["DELETE"](pk)
        return JSONResponse(response)
