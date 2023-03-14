from sqlalchemy import Table


def make_json_object(table: Table, result) -> dict:
    fields = [column.key for column in table.columns]
    content = {field: result[field] for field in fields}
    return content


responses = {
    "GET_one": make_json_object,
    "GET_all": lambda table, results: [
        make_json_object(table, result) for result in results
    ],
    "PUT": lambda id: f"Successfully updated item with id {id}".format(id),
    "DELETE": lambda id: f"Successfully deleted item with id {id}".format(id),
    "POST": lambda id: f"Successfully created item with id {id}".format(id),
}

error_responses = {
    "GET": "Error getting object(s).",
    "PUT": "Error updating objects.",
    "DELETE": "Error deleting objects.",
    "POST": "Error creating object.",
}
