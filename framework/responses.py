
def get_json_object(table, result):
    fields = [column.key for column in table.columns]
    content = {
        field: result[field] for field in fields
    }  
    return content


def get_json_objects(table, results):
    fields = [column.key for column in table.columns]       
    content = [
        {
            field: result[field] for field in fields
        }
        for result in results
        ]
    
    return content



responses = {
    'GET_one': get_json_object,
    'GET_all': get_json_objects,
    'PUT': lambda id: f"Successfully updated item with id {id}".format(id),
    'DELETE':  lambda id: f"Successfully deleted item with id {id}".format(id),
    'POST': lambda id: "Successfully created item."
}