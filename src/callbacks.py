import dash
import base64
import json
from dash.dependencies import Input, Output, State
from dash import html
from callback_helpers import give_me_the_odds, add_random_images, add_node_bhunters, \
    add_node_death_star, get_graph_from_sqlite
from r2d2_c3po_brain import build_hash_bhunters


def register_callbacks(app):
    """
    Register all the necessary callbacks for the Dash application to manage updates, user interactions,
    and data processing.

    :param app: The Dash application instance to which the callbacks are registered.
    """

    # Callback to update images based on base64 input data
    @app.callback(
        [Output('output-message', 'children')],
        [Input('im64', 'data')],
        prevent_initial_call=True
    )
    def update_images(img_base64_1):
        """
        Update the displayed images in the output message area.

        :param img_base64_1: Base64-encoded string representing the image to be displayed.

        :return: List of HTML image elements to be rendered.
        """
        return [html.Div([
            html.Img(
                src='/assets/c3po.png',
                style={'width': '150px', 'height': '120px', 'margin-right': '5px', "margin-top": "5px"}
            ),
            html.Img(
                src=img_base64_1,
                style={'width': '1000px', 'height': '100px', 'margin-right': '5px', "margin-top": "5px"}
            )
        ])]

    # Callback to compute the path and update styles based on user input
    @app.callback(
        [
            Output('output-message', 'style'),
            Output("loadingcom", "style", allow_duplicate=True),
            Output('startcomputing', 'data', allow_duplicate=True),
            Output('im64', 'data', allow_duplicate=True)
        ],
        [Input('startcomputing', 'data')],
        [
            State('dbfilepath', 'data'),
            State('nodestart', 'data'),
            State('nodeend', 'data'),
            State("bhunters", 'data'),
            State("autonomy", "data"),
            State("countdown", "data")
        ],
        prevent_initial_call=True
    )
    def compute_path(startcomputing, dbfilepath, nodestart, nodeend, bhunters, autonomy, countdown):
        """
        Compute the optimal path using given parameters and update the UI components.

        :param startcomputing: Boolean indicating whether the computation should start.
        :param dbfilepath: Path to the database file containing graph data.
        :param nodestart: Starting node for the path computation.
        :param nodeend: Ending node for the path computation.
        :param bhunters: Dictionary of bounty hunter presence on planets.
        :param autonomy: Available autonomy or fuel for the journey.
        :param countdown: Maximum allowable travel time or cost.

        :return: Tuple containing updated styles and data states.
        """
        if startcomputing and dbfilepath and nodestart and nodeend and bhunters:
            hmap = {}
            # Convert bounty hunters map to the required format
            for planet, days_dict in bhunters.items():
                hmap[planet] = hmap.get(planet, {})
                for days, present in days_dict.items():
                    hmap[planet][int(days)] = present

            # Compute the odds and get the image
            b64s = give_me_the_odds(dbfilepath, nodestart, nodeend, hmap, countdown, autonomy)
            style = {"display": "flex", "background": "black"}
            return style, {"display": "none"}, False, b64s

        return {"display": "none"}, dash.no_update, startcomputing, ''

    # Callback to handle the 'Compute Path' button click and update styles
    @app.callback(
        [
            Output("loadingcom", "style"),
            Output('compute-path-button', 'n_clicks'),
            Output('startcomputing', 'data'),
            Output('compute-path-button', 'style', allow_duplicate=True)
        ],
        [Input('compute-path-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def computing(n_clicks):
        """
        Handle the compute path button click, triggering computation and style updates.

        :param n_clicks: Number of clicks on the 'Compute Path' button.

        :return: Tuple of updated styles and click data.
        """
        if n_clicks > 0:
            return {
                "display": "flex", "width": "1200px", "background": "black",
                'justify-content': 'center', 'align-items': 'center'
            }, 0, True, {"display": "none"}

        return {"display": "none"}, 0, False, dash.no_update

    # Callback to update the upload display and file state
    @app.callback(
        [
            Output('upload-section', 'style'),
            Output('file-name-text', 'children'),
            Output('file-name-display', 'style'),
            Output('button-container', 'style'),
            Output('remove-file-button', 'n_clicks'),
            Output('graph-data', 'data', allow_duplicate=True),
            Output("output-message", "style", allow_duplicate=True),
            Output('compute-path-button', 'style', allow_duplicate=True),
            Output("loadingcom", "style", allow_duplicate=True)
        ],
        [Input('uploaded-filename', 'data'), Input('remove-file-button', 'n_clicks')],
        [State('file-name-display-1', 'style'), State('button-container', 'style')],
        prevent_initial_call=True
    )
    def update_upload_display(filename, n_clicks_remove, style_other_file, style_button):
        """
        Update the upload display when a file is uploaded or removed.

        :param filename: Name of the uploaded file.
        :param n_clicks_remove: Number of clicks on the 'Remove File' button.
        :param style_other_file: Style of the other file display section.
        :param style_button: Style of the button container.

        :return: Tuple of updated styles, file states, and button states.
        """
        if n_clicks_remove > 0:
            # Reset display when file is removed
            return {'display': 'block'}, '', {'display': 'none'}, {'display': 'none'}, 0, {}, {'display': 'none'},\
                {'background': 'black'}, {'display': 'none'}

        if filename:
            # Show uploaded file details and update button visibility
            if style_other_file != {'display': 'none'}:
                style_button = {'display': 'flex'}
            return {'display': 'none'}, f"{filename}", {'display': 'block', 'background': 'black'},\
                style_button, 0, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        return {'display': 'block'}, '', {'display': 'none'}, {'display': 'none'}, 0,\
            dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Callback to handle second upload section updates
    @app.callback(
        [
            Output('upload-section-1', 'style'),
            Output('file-name-text-1', 'children'),
            Output('file-name-display-1', 'style'),
            Output('remove-file-button-1', 'n_clicks'),
            Output('button-container', 'style', allow_duplicate=True),
            Output('countdown', 'data', allow_duplicate=True),
            Output('bhunters', 'data', allow_duplicate=True),
            Output('graph-data', 'data', allow_duplicate=True),
            Output("output-message", "style", allow_duplicate=True),
            Output('compute-path-button', 'style', allow_duplicate=True),
            Output("loadingcom", "style", allow_duplicate=True)
        ],
        [Input('uploaded-filename-1', 'data'), Input('remove-file-button-1', 'n_clicks')],
        [State('graph-data', 'data'), State('file-name-display', 'style'), State('button-container', 'style')],
        prevent_initial_call=True
    )
    def update_upload_display_2(filename, n_clicks_remove, graph_data, style_other_file, style_button):
        """
        Update the second upload display section based on user interactions.

        :param filename: Name of the uploaded file.
        :param n_clicks_remove: Number of clicks on the 'Remove File' button.
        :param graph_data: Current graph data being processed.
        :param style_other_file: Style of the other file display section.
        :param style_button: Style of the button container.

        :return: Tuple of updated styles, data states, and button states.
        """
        if n_clicks_remove > 0:
            if graph_data:
                # Reset graph data when file is removed
                graph_data = add_node_bhunters(graph_data, {})

            return {'display': 'block'}, '', {'display': 'none'}, 0, {'display': 'none'}, 0, {}, graph_data, {
                "display": "none"}, {'background': 'black'}, {"display": "none"}

        if filename:
            # Show uploaded file details and update button visibility
            if style_other_file == {'display': 'block', 'background': 'black'}:
                style_button = {'display': 'flex'}
            return {'display': 'none'}, f"{filename}", {'display': 'block', 'background': 'black'}, 0,\
                style_button, dash.no_update, dash.no_update, graph_data, dash.no_update, dash.no_update, dash.no_update

        return {'display': 'block'}, '', {'display': 'none'}, 0, \
            style_button, dash.no_update, dash.no_update, graph_data, dash.no_update, dash.no_update, dash.no_update

    # Callback to update the graph elements displayed in the cytoscape component
    @app.callback(
        Output('cytoscape-graph', 'elements'),
        [Input('graph-data', 'data')]
    )
    def update_graph(graph_data):
        """
        Update the elements of the cytoscape graph based on the provided graph data.

        :param graph_data: Dictionary containing nodes and edges for the graph.

        :return: List of elements to be rendered in the cytoscape graph.
        """
        if graph_data:
            elements = graph_data['elements']
            return elements
        else:
            return []

    # Callback to handle file upload and update the first file's state and data
    @app.callback(
        [
            Output('graph-data', 'data'),
            Output('uploaded-filename', 'data'),
            Output('upload-data', 'filename'),
            Output('upload-data', 'contents'),
            Output('nodestart', 'data', allow_duplicate=True),
            Output('autonomy', 'data', allow_duplicate=True),
            Output('nodeend', 'data', allow_duplicate=True),
            Output('dbfilepath', 'data')
        ],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename'), State('bhunters', 'data')],
        prevent_initial_call=True
    )
    def upload_and_submit_file1(contents, filename, bhunters):
        """
        Process the uploaded file and extract graph data for the first upload section.

        :param contents: Base64-encoded string of the file contents.
        :param filename: Name of the uploaded file.
        :param bhunters: Dictionary of bounty hunter presence on planets.

        :return: Tuple containing updated graph data, file states, and extracted mission details.
        """
        if contents:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            try:
                graph_json = json.loads(decoded)

                db_file_location = graph_json['routes_db']
                nodestart = graph_json['departure']
                nodeend = graph_json['arrival']
                autonomy = graph_json['autonomy']

                # Retrieve and process graph data
                graph_data = get_graph_from_sqlite(db_file_location, nodestart, nodeend)

                graph_data = add_node_death_star(graph_data, nodeend)
                graph_data = add_random_images(graph_data, nodestart)  # Add images to nodes

                if bhunters:
                    graph_data = add_node_bhunters(graph_data, bhunters)

                return graph_data, filename, None, None, nodestart, autonomy, nodeend, db_file_location
            except Exception as e:
                print(e)
                return {}, '', None, None, dash.no_update, dash.no_update, dash.no_update, dash.no_update

        return {}, '', None, None, [], dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Callback to handle file upload and update the second file's state and data
    @app.callback(
        [
            Output('uploaded-filename-1', 'data'),
            Output('upload-data-1', 'filename'),
            Output('upload-data-1', 'contents'),
            Output('countdown', 'data', allow_duplicate=True),
            Output('bhunters', 'data'),
            Output('graph-data', 'data', allow_duplicate=True)
        ],
        [Input('upload-data-1', 'contents')],
        [State('upload-data-1', 'filename'), State('graph-data', 'data')],
        prevent_initial_call=True
    )
    def upload_and_submit_file2(contents, filename, graph_data):
        """
        Process the uploaded file and extract graph data for the second upload section.

        :param contents: Base64-encoded string of the file contents.
        :param filename: Name of the uploaded file.
        :param graph_data: Current graph data being processed.

        :return: Tuple containing updated file states, countdown data, and bounty hunter details.
        """
        if contents:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            try:
                dic_data = json.loads(decoded)
                countdown = dic_data["countdown"]
                bhuntersmap = dic_data["bounty_hunters"]
                hashunt = build_hash_bhunters(bhuntersmap)

                if graph_data:
                    graph_data = add_node_bhunters(graph_data, hashunt)

                return filename, None, None, countdown, hashunt, graph_data
            except Exception as e:
                print(e)
                return '', None, None, 0, {}, graph_data

        return '', None, None, 0, {}, graph_data

    # Callback to update the stylesheet for the countdown edge label
    @app.callback(
        Output('cytoscape-graph', 'stylesheet', allow_duplicate=True),
        [Input('countdown', 'data')],
        [State('cytoscape-graph', 'stylesheet')],
        prevent_initial_call=True
    )
    def update_edge_label(countdown, stylesheet):
        """
        Update the edge label in the cytoscape graph based on the countdown data.

        :param countdown: Current countdown data to be displayed on the graph edge.
        :param stylesheet: Current stylesheet of the cytoscape graph.

        :return: Updated stylesheet with the new countdown label.
        """
        if countdown:
            new_stylesheet = stylesheet + [
                {
                    'selector': 'edge[id = "DSS"]',
                    'style': {
                        'label': str(countdown)
                    }
                }
            ]

            return new_stylesheet

        return stylesheet

    # Callback to update the stylesheet for the starting node
    @app.callback(
        Output('cytoscape-graph', 'stylesheet', allow_duplicate=True),
        [Input('nodestart', 'data'), Input('autonomy', 'data')],
        [State('cytoscape-graph', 'stylesheet')],
        prevent_initial_call=True
    )
    def update_node_start(nodestart, autonomy, stylesheet):
        """
        Update the appearance of the starting node in the cytoscape graph.

        :param nodestart: ID of the starting node.
        :param autonomy: Available autonomy for the journey.
        :param stylesheet: Current stylesheet of the cytoscape graph.

        :return: Updated stylesheet with the new start node styling.
        """
        if nodestart and autonomy:
            new_stylesheet = stylesheet + [
                {
                    'selector': f"node[id = '{nodestart}']",
                    'style': {
                        'background-opacity': 0,
                        'border-width': 1,
                        'border-color': 'blue',
                        'width': 60,
                        'height': 60,
                        'label': f'{nodestart}: start, autonomy: {autonomy}',
                        'font-size': 10,
                        'color': 'blue'
                    }
                }
            ]

            return new_stylesheet

        return stylesheet
