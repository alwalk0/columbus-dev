from sqlalchemy import Table

import yaml
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, PlainTextResponse
from starlette.routing import Route

from .queries import raw_queries
from .responses import responses, error_responses
from .utils import do_database_setup


database, database_tables = do_database_setup()


def create_app(apis) -> Starlette:
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
    table_name = specs["table"]
    methods = specs["methods"]
    url = "/" + str(table_name)
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


async def get_request(request: Request, table: Table) -> Response:
    try:
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
    except Exception as e:
        return Response(content=error_responses["GET"])


async def post_request(request: Request, table: Table) -> Response:
    try:
        data = await request.json()
        query = table.insert().values(data)
        result = await database.execute(query)
        response = responses["POST"](result)
        return JSONResponse(response)
    except Exception as e:
        return Response(content=error_responses["POST"])


async def put_request(request: Request, table: Table) -> Response:
    try:
        data = await request.json()
        query = raw_queries["PUT"](table)
        pk = pk = request.path_params["id"]
        values = {"id": pk} | data
        result = await database.execute(query=query, values=values)
        response = responses["PUT"](pk)
        return JSONResponse(response)
    except Exception as e:
        return Response(content=error_responses["PUT"])


async def delete_request(request: Request, table: Table) -> Response:
    try:
        query = raw_queries["DELETE"](table)
        pk = request.path_params["id"]
        result = await database.execute(query=query, values={"id": pk})
        response = responses["DELETE"](pk)
        return JSONResponse(response)
    except Exception as e:
        return Response(content=error_responses["DELETE"])
