from src.database.database_setup import PathTable

#Retrieve customer path
def get_customer_path_points(customer_id):
    query = (
        PathTable
        .select()
        .where(PathTable.customer_id == customer_id)
    )
    return list(query)

#validate pathPoints sorted with inc timestamps
def sort_path_points(path_points):
    return sorted(path_points, key=lambda p: p.timestamp)

#Convert path rows into coordinate tuples for easier path processing
def convert_to_coordinates(path_points):
    coordinates = []
    for p in path_points:
        coordinates.append([p.location_x, p.location_y])

    return coordinates

#Build customer path from path points
def construct_path(customer_id):
    points = get_customer_path_points(customer_id)

    if not points:
        return []

    sorted_points = sort_path_points(points)

    path = convert_to_coordinates(sorted_points)

    return path


