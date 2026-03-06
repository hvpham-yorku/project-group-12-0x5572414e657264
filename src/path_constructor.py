from src.database.database_setup import PathTable

#Retrieve customer path
def get_customer_path_points(customer_id):
    query = (
        PathTable
        .select()
        .where(PathTable.customer_id == customer_id)
    )
    return list(query)

#