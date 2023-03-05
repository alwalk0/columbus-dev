from databases import Database
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from .queries import raw_queries
from .responses import responses

async def get_request(request, database, table):

    if request.query_params:
        query = raw_queries['GET_one'](table)
        pk = int(request.query_params['id'])
        result = await database.fetch_one(query=query, values={"id": pk})     
        response =  JSONResponse(responses['GET_one'](table, result))       
    else:           
        query = table.select()
        results = await database.fetch_all(query)
        response =  JSONResponse(responses['GET_all'](table, results))

    return response    


async def post_request(request, database, table):
    data = await request.json()
    query = table.insert().values(data)
    result = await database.execute(query)
    response = responses['POST']()
    return JSONResponse(response)


async def put_request(request, database, table):
    data = await request.json()
    if request.query_params:
        query = raw_queries['PUT'](table)
        pk = int(request.query_params['id'])
        values = {"id": pk} | data
        result = await database.execute(query=query, values=values)
        response = responses['PUT'](pk)
        return JSONResponse(response)


async def delete_request(request, database, table):
    if request.query_params:
        query = raw_queries['DELETE'](table)
        pk = int(request.query_params['id'])
        result = await database.execute(query=query, values={"id": pk})
        response = responses['DELETE'](pk)
        return JSONResponse(response)