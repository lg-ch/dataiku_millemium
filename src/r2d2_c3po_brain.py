import json
import click
import sqlite3


def geometric_series_sum(k):
    """
    Calculate the sum of a geometric series with a given ratio and number of terms.

    :param k: The number of terms in the geometric series.

    :return: The sum of the geometric series from 0 to k-1 terms.
    """
    r = 0.9  # Common ratio of the geometric series

    # The formula for the sum of a finite geometric series is:
    # S_k = a * (1 - r^k) / (1 - r), where a is the first term.
    # In this case, a is 1 (i.e., the series starts with 1).
    # Since a = 0.1, and 1 -r is 0.9 the formula simplifies to S_k = (1 - r^k)

    sum_series = 1 - r**k

    return sum_series


def get_bounty_hunters_vertex_schedule(bounty_hunters_map, vertex, days_travelled):
    """
    Retrieve the presence of bounty hunters at a given vertex on a specific day.

    :param bounty_hunters_map: A dictionary mapping planet IDs (vertices) to another dictionary,
                               where each key is a day and the value is an indicator (e.g., 1)
                               of bounty hunter presence.
    :param vertex: The ID of the vertex (planet) being queried.
    :param days_travelled: The number of days that have passed, used to determine the current day of travel.

    :return: An integer indicating the presence of bounty hunters (1 if present, 0 if not) at
    the specified vertex and day.
    """
    # Retrieve and return the bounty hunters' presence from the map.
    # Defaults to 0 if the vertex or day is not found in the map.
    return bounty_hunters_map.get(vertex, {}).get(days_travelled, 0)


def rest_one_day(init, cost, u, autonomy, bounty_hunters_map, stack_dict, min_hunters):
    """
    Simulate resting for one day at a vertex, updating travel costs and bounty hunter encounters.

    :param init: A dictionary mapping cost levels to vertex states, tracking bounty hunter encounters.
    :param cost: The current travel cost or day count.
    :param u: The current vertex (node) being evaluated.
    :param autonomy: The current level of autonomy or fuel remaining.
    :param bounty_hunters_map: A dictionary indicating bounty hunter presence on planets on specific days.
    :param stack_dict: A dictionary used to track changes to vertex states at different costs.
    :param min_hunters: The minimum number of bounty hunter encounters allowed before terminating a path.

    :return: A tuple of updated dictionaries: (init, stack_dict).
    """
    # Ensure that the next cost level has a dictionary for the current vertex
    init[cost + 1] = init.get(cost + 1, {})
    init[cost + 1][u] = init[cost + 1].get(u, {})

    # Iterate over current autonomy states and calculate potential new hunter encounters
    for autonomies, hunterseen in init[cost][u].items():
        # Calculate the number of bounty hunters seen after resting one more day
        bhseen = hunterseen + get_bounty_hunters_vertex_schedule(bounty_hunters_map, str(u), cost + 1)

        # Update the state if it results in fewer hunter encounters and is below the minimum threshold
        if bhseen < init[cost + 1][u].get(autonomy, float('inf')) and bhseen < min_hunters:
            init[cost + 1][u][autonomy] = bhseen

            # Mark the vertex as updated in the stack dictionary for this cost level
            stack_dict[cost + 1] = stack_dict.get(cost + 1, {})
            stack_dict[cost + 1][u] = 1

    return init, stack_dict


def store_vertex(autonomies, weight, init, new_cost, node, bounty_hunters_map, hunterseen,
                 min_hunters, stack_dict, end):
    """
    Update the state of a vertex in the search algorithm, considering autonomy and bounty hunter encounters.

    :param autonomies: The current autonomy level or remaining fuel before moving to the next node.
    :param weight: The cost or weight to travel to the next node.
    :param init: A dictionary tracking vertex states across different cost levels,
    with autonomy levels and hunter encounters.
    :param new_cost: The updated travel cost or time after moving to the next node.
    :param node: The current node being evaluated in the path.
    :param bounty_hunters_map: A dictionary mapping nodes and days to bounty hunter presence.
    :param hunterseen: The cumulative number of bounty hunters encountered so far.
    :param min_hunters: The minimum number of acceptable bounty hunter encounters.
    :param stack_dict: A dictionary used to manage vertices that need reevaluation in the algorithm.
    :param end: The destination node for the journey.

    :return: A tuple of updated dictionaries (init, stack_dict) and the updated min_hunters value.
    """
    # Calculate new autonomy after moving to the next node
    new_autonomy = autonomies - weight

    # Initialize state for the node at the new cost level if not already present
    init[new_cost] = init.get(new_cost, {})
    init[new_cost][node] = init[new_cost].get(node, {})

    # Calculate the number of bounty hunters seen after moving to the node
    bhseen = hunterseen + get_bounty_hunters_vertex_schedule(bounty_hunters_map, node, new_cost)

    # Update the state if it results in fewer hunter encounters and is below the minimum threshold
    if bhseen < init[new_cost][node].get(new_autonomy, float('inf')) and bhseen < min_hunters:
        init[new_cost][node][new_autonomy] = bhseen

        # Mark the node as updated in the stack dictionary for this cost level
        stack_dict[new_cost] = stack_dict.get(new_cost, {})
        stack_dict[new_cost][node] = 1

    # If the node is the destination, update the minimum number of hunters seen
    if node == end:
        min_hunters = min(min_hunters, init[new_cost][node].get(new_autonomy, float('inf')))

    return init, stack_dict, min_hunters


def find_path_with_minimal_ennemies_before_countdown(graph, start, end, max_cost, autonomy, bounty_hunters_map):
    """
    Find the path with the minimal number of bounty hunter encounters before a specified countdown.

    :param graph: A dictionary representing the graph as an adjacency list, where each key is a node and
                  the value is a list of tuples (neighbor, weight).
    :param start: The starting node ID for the journey.
    :param end: The ending node ID for the journey.
    :param max_cost: The maximum cost (or time) allowed to complete the journey.
    :param autonomy: The initial autonomy (or fuel) available for the journey.
    :param bounty_hunters_map: A dictionary mapping nodes and days to bounty hunter presence, indicating risk levels.

    :return: An integer representing the minimum number of bounty hunter encounters along the optimal path.
    """
    # Initialize the search state
    init = {0: {start: {autonomy: get_bounty_hunters_vertex_schedule(bounty_hunters_map, start, 0)}}}
    min_hunters = float('inf')  # Track the minimum number of encounters
    stack_dict = {0: {start: 1}}  # Track nodes that need processing

    # if we are there already no need to pursue
    if start == end:
        min_hunters = init[0][start][autonomy]
        max_cost = -1

    # Iterate over each cost level up to the maximum allowed
    for cost in range(max_cost + 1):
        # Remove processed states from previous cost
        if cost:
            stack_dict.pop(cost - 1, 0)

        # Break the loop if there are no nodes left to process
        if not stack_dict:
            break

        # Retrieve and remove the current processing state
        poped = stack_dict.pop(cost, 0)

        if poped:
            # Process each node at the current cost level
            for u in init.get(cost, []):
                if poped.pop(u, 0):
                    # Consider resting for one day
                    if cost + 1 <= max_cost:
                        init, stack_dict = rest_one_day(init, cost, u, autonomy, bounty_hunters_map, stack_dict,
                                                        min_hunters)

                    # Evaluate potential moves to adjacent nodes
                    for v in graph[u]:
                        node = v
                        weight = graph[u][node]
                        new_cost = cost + weight

                        # Check if the move is feasible with current autonomy and within cost constraints
                        if weight <= autonomy and new_cost <= max_cost:
                            prev_autonomies = float('inf')
                            prev_hunterseen = float('inf')

                            # Iterate over possible autonomy states and update paths
                            for autonomies, hunterseen in init[cost][u].items():
                                if prev_hunterseen > hunterseen:
                                    if autonomies >= weight:
                                        init, stack_dict, min_hunters = store_vertex(
                                            autonomies, weight, init, new_cost, node,
                                            bounty_hunters_map, hunterseen, min_hunters, stack_dict, end
                                        )
                                        prev_hunterseen = hunterseen

                                if autonomies > prev_autonomies:
                                    if autonomies >= weight:
                                        init, stack_dict, min_hunters = store_vertex(
                                            autonomies, weight, init, new_cost, node,
                                            bounty_hunters_map, hunterseen, min_hunters, stack_dict, end
                                        )
                                        prev_autonomies = autonomies
    return min_hunters


def get_graph_from_sqlite_r2d2(dbfile, node_end):
    """
    Retrieve graph data from an SQLite database and construct an adjacency list representation.

    This function connects to the specified SQLite database and retrieves all routes stored
    in a table named 'routes'. It assumes that the table contains at least three columns,
    where the first column is the source node, the second column is the target node,
    and the third column is the weight of the edge between these nodes. The function constructs
    an adjacency list representation of the graph and ensures that every node, including the
    specified `node_end`, is initialized in the graph.

    :param dbfile: str - The path to the SQLite database file.
    :param node_end: str - A node that should be initialized in the graph,
                          even if it has no edges.

    :return: dict - A dictionary representing the graph as an adjacency list,
                    where each key is a node, and each value is a dictionary
                    of connected nodes and their respective weights.
    """
    graph = {}

    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(dbfile)

    # Create a cursor and execute a query to fetch all routes
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes")
    rows = cursor.fetchall()

    # Build the adjacency list from the database rows
    for row in rows:
        # Add the edge from source to target with weight
        graph[row[0]] = graph.get(row[0], {})
        graph[row[0]][row[1]] = row[2]

        graph[row[1]] = graph.get(row[1], {})
        graph[row[1]][row[0]] = row[2]

    # Ensure the specified end node is present in the graph
    graph[node_end] = {}
    # Close the database connection
    conn.close()
    return graph


def build_hash_bhunters(bhunters):
    """
    Build a hash map of bounty hunters' presence on different planets over specific days.

    :param bhunters: A list of dictionaries, each containing 'planet' and 'day' keys, representing
                     the planet ID and the day when bounty hunters are present.

    :return: A dictionary mapping each planet ID to another dictionary where each key is a day
             and the value is 1, indicating the presence of bounty hunters on that day.
    """
    hashunters = {}
    for planet in bhunters:
        # Ensure the planet key exists in the hashunters dictionary
        hashunters[planet['planet']] = hashunters.get(planet['planet'], {})

        # Mark the day with bounty hunter presence
        hashunters[planet['planet']][planet["day"]] = 1

    return hashunters


@click.group()
def cli():
    pass


@click.command()
@click.argument('filepath_1')
@click.argument('filepath_2')
def r2d2(filepath_1, filepath_2):
    """
    Calculate and display the probability of successfully reaching a destination in a galaxy traversal scenario.

    :param filepath_1: Path to the JSON file containing the graph and mission details, such as
                       routes database, departure, arrival, and autonomy.
    :param filepath_2: Path to the JSON file containing the empire's information, such as countdown
                       and bounty hunters' presence.

    :return: None. Outputs the success probability percentage to the command line.
    """
    # Load mission details from the first JSON file
    with open(filepath_1, 'r') as milleniumf:
        graph_json = json.load(milleniumf)
        db_file_location = graph_json['routes_db']
        nodestart = graph_json['departure']
        nodeend = graph_json['arrival']
        autonomy = graph_json['autonomy']
        graph = get_graph_from_sqlite_r2d2(db_file_location, nodeend)

    # Load empire information from the second JSON file
    with open(filepath_2, 'r') as empiref:
        hmap = json.load(empiref)
        countdown = hmap["countdown"]
        bhuntersmap = hmap["bounty_hunters"]
        hashunt = build_hash_bhunters(bhuntersmap)

    ennemies = find_path_with_minimal_ennemies_before_countdown(graph, nodestart,
                                                                nodeend, countdown, autonomy, hashunt)

    # Calculate the probability of a successful journey
    proba = 1 - geometric_series_sum(ennemies)
    percentage_proba = round(proba * 100)

    # Output the probability percentage to the command line
    click.echo(percentage_proba)


# Register the r2d2 command
cli.add_command(r2d2)


if __name__ == '__main__':
    cli()
