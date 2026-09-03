import os
import random
import sqlite3
from r2d2_c3po_brain import geometric_series_sum, get_graph_from_sqlite_r2d2, \
    find_path_with_minimal_ennemies_before_countdown
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import time


def generate_c3po_text(probability):
    """
    Generate an image with text simulating C-3PO's dialogue, indicating the probability of success.

    :param probability: An integer representing the probability percentage of a successful journey.

    :return: A base64-encoded PNG image string representing the text.
    """
    # Load the Star Jedi font
    font = ImageFont.truetype("assets/StarJedi-DGRW.ttf", 15)

    # Create a new black image
    img = Image.new('RGB', (1000, 100), color=(0, 0, 0))

    # Initialize the drawing context
    draw = ImageDraw.Draw(img)

    # Default message if probability is zero or not provided
    text = "i am afraid there is 0 percent chance to reach our destination before countdown ...."

    # Update message if a positive probability is given
    if probability:
        text = f"i have found a path across the stars with {probability} percent chance of not being caught"

    # Draw the text onto the image
    draw.text((50, 50), text, font=font, fill=(255, 255, 255))

    # Save the image to a bytes buffer
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")

    # Encode the image in base64
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"


def give_me_the_odds(dbfile_location, start, end, bounty_hunters_map, countdown, refuel_value):
    """
    Calculate the odds of a successful journey and generate a C-3PO styled message as a base64-encoded image.

    :param dbfile_location: Path to the SQLite database file containing the graph data.
    :param start: The starting node ID for the journey.
    :param end: The ending node ID for the journey.
    :param bounty_hunters_map: A dictionary mapping planet IDs to lists of days indicating bounty hunter presence.
    :param countdown: An integer representing the number of days available for the journey.
    :param refuel_value: An integer representing the refueling cost or value considered in path calculation.

    :return: A base64-encoded PNG image string with a message indicating the probability of a successful journey.
    """
    # just to see the logo of the empire loading
    time.sleep(3)
    # Retrieve the graph from the SQLite database
    graph = get_graph_from_sqlite_r2d2(dbfile_location, end)

    # Calculate the minimal number of enemies
    ennemies = find_path_with_minimal_ennemies_before_countdown(graph, start, end, countdown, refuel_value,
                                                                bounty_hunters_map)

    # Calculate the probability of success as a percentage
    proba = int((1 - geometric_series_sum(ennemies)) * 100)

    # Generate a C-3PO styled message as an image
    b64s = generate_c3po_text(proba)

    return b64s


def add_random_images(graph_data, start):
    """
    Assign random images to nodes in the graph data, with special images for "DeathStar" and the start node.

    :param graph_data: A dictionary containing the graph's data with an 'elements' key (list of nodes and edges).
    :param start: The ID of the start node that should receive a specific image.

    :return: Updated graph data with images assigned to the nodes.
    """
    # Get image URLs from specified directories
    image_urls = [f'/assets/planets/{planet_file}' for planet_file in os.listdir('assets/planets')]
    millenium_image_urls = [f'/assets/planets_millenium/{planet_file}'
                            for planet_file in os.listdir('assets/planets_millenium')]

    for element in graph_data['elements']:
        if 'source' not in element['data']:  # It's a node
            element['data']['image'] = random.choice(image_urls)
        if 'source' not in element['data'] and element['data']['id'] == "DS":
            element['data']['image'] = '/assets/deathstar.png'
        if 'source' not in element['data'] and start == element['data']['id']:
            element['data']['image'] = random.choice(millenium_image_urls)

    return graph_data


def add_node_death_star(graph_data, terminal_node):
    """
    Add a "DeathStar" node and a directed edge to the specified terminal node in the graph data.

    :param graph_data: A dictionary containing the graph's data with an 'elements' key (list of nodes and edges).
    :param terminal_node: The ID of the target terminal node.

    :return: Updated graph data with the new "DeathStar" node and edge.
    """
    if 'elements' in graph_data:
        # Add the "DeathStar" node and an edge to the terminal node
        graph_data['elements'] += [
            {"data": {"id": "DS", "label": "DeathStar"}},
            {"data": {"id": "DSS", "source": "DS", "target": terminal_node, "weight": 0}}
        ]
    return graph_data


def add_node_bhunters(graph_data, bhunters):
    """
    Add "Bounty Hunters" nodes and edges to the graph data, linking to specified planets with day labels.

    :param graph_data: A dictionary containing the graph's data with keys like 'start' and 'elements'.
    :param bhunters: A dictionary where keys are planet IDs and values are lists of days indicating hunter presence.

    :return: A new graph data dictionary with added "Bounty Hunters" nodes and edges.
    """
    new_graph_data = {}

    # Retain the start node if it exists
    if "start" in graph_data:
        new_graph_data["start"] = graph_data["start"]

    if 'elements' in graph_data:
        new_graph_data["elements"] = []

        # Copy nodes and edges, excluding bounty hunter nodes
        for elements in graph_data['elements']:
            if "source" not in elements['data'] and not elements['data']['id'].startswith('HUNTERS'):
                new_graph_data["elements"] += [elements]
            if "source" in elements['data']:
                new_graph_data["elements"] += [elements]

        # Add the main Bounty Hunters node if there are hunters specified
        if bhunters:
            new_graph_data['elements'].append(
                {"data": {"id": "HUNTERS", "label": "BountyHunters", "image": "/assets/bhunters.png"}}
            )

        # Add nodes and edges for each planet with bounty hunters
        # check that the planet exists in the cyto-graph
        for planet, days in bhunters.items():
            for elements in new_graph_data['elements']:
                if "source" not in elements['data'] and elements['data']['id'] == planet:
                    # Create a comma-separated label of days
                    days_list_label = ','.join(str(day) for day in days)
                    new_graph_data['elements'].append({
                        "data": {
                            "id": f"HUNTERS_{planet}",
                            "source": "HUNTERS",
                            "target": planet,
                            "label": days_list_label
                        }
                    })

    return new_graph_data


def get_graph_from_sqlite(dbfile, startnode, endnode):
    """
    Retrieve graph data from an SQLite database and construct a graph dictionary with nodes and edges.

    The function connects to an SQLite database containing a table 'routes', where each row
    represents a directed edge in a graph with a source node, target node, and an edge weight.
    The function creates a dictionary representation of this graph, including only a specified
    number of nodes and edges, ensuring the start and end nodes are included. At the moment only
    12 nodes and 25 edges can be represented.

    :param dbfile: Path to the SQLite database file.
    :param startnode: The node ID representing the start node that must be included in the graph.
    :param endnode: The node ID representing the end node that must be included in the graph.

    :return: A dictionary representing the graph, with 'elements' as a list of nodes and edges.
             Each element is a dictionary containing 'data' with 'id' and 'label' for nodes,
             and 'source', 'target', 'weight', and 'label' for edges.
    """
    graph = {}

    # Connect to the SQLite database
    conn = sqlite3.connect(dbfile)

    # Create a cursor and execute a query to fetch all routes from the 'routes' table
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes")
    rows = cursor.fetchall()

    # Initialize the graph structure and helper structures to track seen nodes and edges
    graph["elements"] = []
    seen = {}  # Track nodes that have already been added
    seen_edge = []  # Track edges that have already been added to avoid duplicates

    # Limits for the total number of nodes and edges to include in the graph
    total_nodes = 12
    total_edges = 25

    for row in rows:
        # Each row is expected to have the format: (source, target, weight)

        # Add the source node if it hasn't been added yet and conditions allow
        if (seen.get(row[0], 1) and row[0] == startnode) or (seen.get(row[0], 1) and total_nodes > 0) \
                or (seen.get(row[0], 1) and row[0] == endnode):
            node = {'data': {"id": row[0], "label": row[0]}}
            seen[row[0]] = 0
            graph["elements"].append(node)
            total_nodes -= 1

        # Add the target node if it hasn't been added yet and conditions allow
        if (seen.get(row[1], 1) and row[1] == startnode) or (seen.get(row[1], 1) and total_nodes > 0) \
                or (seen.get(row[1], 1) and row[1] == endnode):
            node = {'data': {"id": row[1], "label": row[1]}}
            seen[row[1]] = 0
            graph["elements"].append(node)
            total_nodes -= 1

        # Add the edge if it hasn't been added yet, and conditions allow
        if (row[0], row[1]) not in seen_edge and total_edges > 0 and not seen.get(row[0], 1) and not seen.get(row[1],
                                                                                                              1):
            edge = {'data': {"source": row[0], "target": row[1], "weight": row[2], "label": str(row[2])}}
            seen_edge.append((row[0], row[1]))
            seen_edge.append((row[1], row[0]))  # Treat edges as undirected
            graph["elements"].append(edge)
            total_edges -= 1

    # Close the database connection
    conn.close()

    return graph
