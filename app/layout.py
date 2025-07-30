from dash import html, dcc
import dash_bootstrap_components as dbc

layout = dbc.Container([
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    html.A(
                        html.Img(src='assets/f1-logo.png', style={'height': '80px', 'cursor': 'pointer'}),
                        href='https://www.formula1.com',
                        target='_blank',
                        rel='no opener no referrer'
                    ),
                    width="auto",
                    className="d-flex align-items-center",
                    style={'padding-right': '10px'}
                ),
                dbc.Col(
                    html.H1("F1 Telemetry Lap Comparison", className="text-white m-0"),
                    className="d-flex align-items-center"
                )
            ], align="center", className="mb-3 g-0"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Year:", className="text-white"),
                    dbc.Input(id='year-input', type='number', value=2024, min=2018, max=2025),
                ], width=2),
                dbc.Col([
                    dbc.Label("Round:", className="text-white"),
                    dbc.Input(id='round-input', type='number', value=17, min=1, max=25),
                ], width=2),
                dbc.Col([
                    dbc.Label("Session Type:", className="text-white"),
                    dcc.Dropdown(
                        id='session-type',
                        options=[
                            {'label': 'FP1', 'value': 'FP1'},
                            {'label': 'FP2', 'value': 'FP2'},
                            {'label': 'FP3', 'value': 'FP3'},
                            {'label': 'Qualifying (Q)', 'value': 'Q'},
                            {'label': 'Sprint (S)', 'value': 'S'},
                            {'label': 'Race (R)', 'value': 'R'}
                        ],
                        value='Q',
                        clearable=False,
                        style={'color': '#000000'}  # To make text visible inside dropdown
                    ),
                ], width=3),
                dbc.Col([
                    html.Br(),
                    dbc.Button("Load Session", id='load-button', n_clicks=0, color='danger'),
                ], width=2,className="d-flex align-items-end")
            ], className="mb-3"),
        ])
    ], color="dark", className="mb-4"),

    # Dropdowns
    dbc.Row([
        dbc.Col([
            dbc.Label("Select Drivers:", id='driver-label', className="text-white", style={'display': 'none'}),
            dcc.Dropdown(id='driver-dropdown', multi=True, options=[], value=[], style={'display': 'none'}),
        ], width=6),
        dbc.Col([
            dbc.Label("Select Telemetry Channel:", id='telemetry-label', className="text-white", style={'display': 'none'}),
            dcc.Dropdown(
                id='telemetry-type',
                options=[
                    {'label': 'Speed', 'value': 'Speed'},
                    {'label': 'Throttle', 'value': 'Throttle'},
                    {'label': 'Brake', 'value': 'Brake'},
                    {'label': 'RPM', 'value': 'RPM'},
                    {'label': 'Gear', 'value': 'nGear'},
                    {'label': 'DRS', 'value': 'DRS'}
                ],
                value='Speed',
                clearable=False,
                style={'width': '100%', 'display': 'none'}
            ),
        ], width=6),
    ], className="mb-4"),

    html.Div(id='session-store', style={'display': 'none'}),

    # Plot
    dbc.CardBody([
        dcc.Loading(
            dcc.Graph(id='telemetry-plot'),
            type='circle'
        ),
        dcc.Loading(
            dcc.Graph(id='track-map'),
            type='circle'
        )
    ])
], fluid=True, className="bg-dark p-4")
