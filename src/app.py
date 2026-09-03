import dash
import dash_cytoscape as cyto
from dash import html
from dash import dcc
from callbacks import register_callbacks

# Configuration of Dash
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    # Stores for managing session state and data
    dcc.Store(id='session-id', storage_type='session'),
    dcc.Store(id='node-index', data=-1),
    dcc.Store(id='uploaded-filename', data=''),
    dcc.Store(id='uploaded-filename-1', data=''),
    dcc.Store(id='bhunters', data={}),
    dcc.Store(id='countdown', data=0),
    dcc.Store(id='startcomputing', data=False),
    dcc.Store(id='nodeend', data=''),
    dcc.Store(id='nodestart', data=''),
    dcc.Store(id='graph-data', data={}),
    dcc.Store(id='im64', data=''),
    dcc.Store(id='autonomy', data=0),
    dcc.Store(id='dbfilepath', data=''),

    # Cytoscape component for graph visualization
    cyto.Cytoscape(
        id='cytoscape-graph',
        layout={'name': 'cose'},
        style={
            'width': '100%',
            'height': '800px',
            'background-image': 'url(/assets/img.png)',
            'background-size': 'cover',
            'background-position': 'center'
        },
        elements=[],  # Initial empty list of elements
        stylesheet=[
            {
                'selector': 'node',
                'style': {
                    'label': 'data(label)',
                    'background-fit': 'cover',
                    'background-image': 'data(image)',
                    'background-opacity': 0,
                    'width': 40,
                    'height': 40,
                    'font-size': 10,
                    'color': 'white'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'label': 'data(label)',
                    'line-color': 'white',
                    'width': '1',
                    'font-size': 10,
                    'color': 'red',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -10
                }
            },
            {
                'selector': 'edge[id ^= "HUNTERS"]',
                'style': {
                    'label': 'data(label)',
                    'line-color': 'red',
                    'width': '1',
                    'font-size': 10,
                    'color': 'red',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -10
                }
            },
        ]
    ),

    # Section for file uploads
    html.Div(id='upload-divs', children=[
        html.Div(id='upload-section', children=[
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select a File for millennium falcon road and autonomy')
                ]),
                style={
                    'width': '45%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            )
        ]),
        html.Div(id='upload-section-1', children=[
            dcc.Upload(
                id='upload-data-1',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select a File for bounty hunters road and countdown')
                ]),
                style={
                    'width': '45%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            )
        ])
    ]),

    # Display area for file names and control buttons
    html.Div(id="double-file-name-display", style={
        'display': 'flex',
        'gap': '10px',
        'margin-top': '20px'
    }, children=[
        html.Div(id='file-name-display', style={'display': 'none'}, children=[
            html.Img(src='/assets/xwing.png', style={'width': '90px', 'height': '90px', 'margin-right': '5px'}),
            html.Span(id='file-name-text', style={'color': 'white'}),
            html.Button('✖', id='remove-file-button', n_clicks=0, style={
                'background': 'none',
                'border': 'none',
                'color': 'red',
                'font-size': '16px',
                'cursor': 'pointer',
                'margin-left': '10px'
            })
        ]),
        html.Div(id='file-name-display-1', style={'display': 'none'}, children=[
            html.Img(src='/assets/tie_fighter.png', style={'width': '90px', 'height': '90px', 'margin-right': '5px'}),
            html.Span(id='file-name-text-1', style={'color': 'white'}),
            html.Button('✖', id='remove-file-button-1', n_clicks=0, style={
                'background': 'none',
                'border': 'none',
                'color': 'red',
                'font-size': '16px',
                'cursor': 'pointer',
                'margin-left': '10px'
            })
        ]),
        html.Div(
            id='button-container',
            style={'display': 'none'},
            children=[
                html.Button(
                    id='compute-path-button',
                    n_clicks=0,
                    style={'background': 'black'},
                    children=[
                        html.Img(src='/assets/c3po.png', style={
                            'width': '150px',
                            'height': '120px',
                            'margin-right': '5px'
                        }),
                        html.Img(src='/assets/todds.png', style={
                            'width': '1000px',
                            'height': '60px',
                            'margin-right': '5px'
                        })
                    ]
                ),
                html.Div(id='output-message', style={"display": "none"}, children=[
                    html.Img(src='/assets/c3po.png', style={
                        'width': '150px',
                        'height': '120px',
                        'margin-right': '5px',
                        "margin-top": "5px"
                    })
                ]),
                html.Div(id='loadingcom', style={"display": "none"}, children=[
                    html.Img(src='/assets/empireload.gif', style={
                        'width': '120px',
                        'height': '120px',
                        'margin-right': '5px'
                    })
                ]),
            ]
        )
    ]),
])

register_callbacks(app)

if __name__ == '__main__':
    app.run_server()
