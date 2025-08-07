from dash import html, dcc, dash_table
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
        dbc.Row([
            dbc.Col([
                dbc.Label("Select Laps:", id='lap-label', className="text-white", style={'display': 'none'}),
                dcc.Dropdown(id='lap-dropdown', multi=True, options=[], value=[], style={'display': 'none'}),
            ], width=6),
        ], className="mb-4"),
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
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    dbc.Row([
                        dbc.Col(html.H5("Telemetry Plot", className="mb-0"), width="auto"),
                        dbc.Col(
                            html.Button("▼", id={"type": "collapse-toggle", "section": "telemetry"}, className="btn btn-sm btn-secondary",
                                        n_clicks=0),
                            width="auto",
                            style={"textAlign": "right"}
                        )
                    ], justify="between")
                ),
                dbc.Collapse(
                    dbc.CardBody([
                        dcc.Graph(id='telemetry-plot')
                    ]),
                    id={"type": "collapse-body", "section": "telemetry"},
                    is_open=True
                )
            ], color="dark", inverse=True, className="shadow-sm mb-4")
        ], width=12),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    dbc.Row([
                        dbc.Col(html.H5("Track Map", className="mb-0"), width="auto"),
                        dbc.Col(
                            html.Button("▼", id={"type": "collapse-toggle", "section": "track"}, className="btn btn-sm btn-secondary",
                                        n_clicks=0),
                            width="auto",
                            style={"textAlign": "right"}
                        )
                    ], justify="between")
                ),
                dbc.Collapse(
                    dbc.CardBody([
                        dcc.Graph(id='track-map')
                    ]),
                    id={"type": "collapse-body", "section": "track"},
                    is_open=True
                )
            ], color="dark", inverse=True, className="shadow-sm mb-4")
        ], width=12),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Lap Time Deltas"),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id='lap-delta-table',
                            columns=[
                                {"name": "Driver", "id": "Driver"},
                                {"name": "Lap Time", "id": "LapTime"},
                                {"name": "Delta (s)", "id": "Delta"},
                                {"name": "Compound", "id": "Compound"},
                            ],
                            style_cell={'textAlign': 'center', 'color': 'white', 'backgroundColor': '#222'},
                            style_header={'fontWeight': 'bold', 'backgroundColor': '#444', 'color': 'white'},
                            style_data_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{Delta} > 0',
                                        'column_id': 'Delta'
                                    },
                                    'color': 'red',
                                },
                                {
                                    'if': {
                                        'filter_query': '{Delta} <= 0',
                                        'column_id': 'Delta'
                                    },
                                    'color': 'lime',
                                },
                                    {
                                        'if': {'filter_query': '{Compound} = "SOFT"', 'column_id': 'Compound'},
                                        'backgroundColor': '#FF7F7F',
                                        'color': 'black'
                                    },
                                    {
                                        'if': {'filter_query': '{Compound} = "MEDIUM"', 'column_id': 'Compound'},
                                        'backgroundColor': '#FFD966',
                                        'color': 'black'
                                    },
                                    {
                                        'if': {'filter_query': '{Compound} = "HARD"', 'column_id': 'Compound'},
                                        'backgroundColor': '#A9D18E',
                                        'color': 'black'
                                    },
                                    {
                                        'if': {'filter_query': '{Compound} = "INTER"', 'column_id': 'Compound'},
                                        'backgroundColor': '#5BC0DE',
                                        'color': 'black'
                                    },
                                    {
                                        'if': {'filter_query': '{Compound} = "WET"', 'column_id': 'Compound'},
                                        'backgroundColor': '#4472C4',
                                        'color': 'white'
                                    }
                            ],
                            style_table={'overflowX': 'auto'},
                            page_size=10,
                        )
                    ])
                ], color="dark", inverse=True, className="mb-4 shadow-sm"),
                width=12
            ),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    dbc.Row([
                        dbc.Col(html.H5("Weather Chart", className="mb-0"), width="auto"),
                        dbc.Col(
                            html.Button("▼", id={"type": "collapse-toggle", "section": "weather"}, className="btn btn-sm btn-secondary",
                                        n_clicks=0),
                            width="auto",
                            style={"textAlign": "right"}
                        )
                    ], justify="between")
                ),
                dbc.Collapse(
                    dbc.CardBody([
                        dcc.Graph(id='weather-plot')
                    ]),
                    id={"type": "collapse-body", "section": "weather"},
                    is_open=True
                )
            ], color="dark", inverse=True, className="shadow-sm mb-4")
        ], width=12),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    dbc.Row([
                        dbc.Col(html.H5("Sector Time Comparison", className="mb-0"), width="auto"),
                        dbc.Col(
                            html.Button("▼", id={"type": "collapse-toggle", "section": "sector"}, className="btn btn-sm btn-secondary",
                                        n_clicks=0),
                            width="auto",
                            style={"textAlign": "right"}
                        )
                    ], justify="between")
                ),
                dbc.Collapse(
                    dbc.CardBody([
                        dcc.Graph(id='sector-comparison-chart')
                    ]),
                    id={"type": "collapse-body", "section": "sector"},
                    is_open=True
                )
            ], color="dark", inverse=True, className="shadow-sm mb-4")
        ], width=12),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Sector Comparison Table"),
                dbc.CardBody([
                    dash_table.DataTable(
                        id='sector-comparison-table',
                        columns=[
                            {"name": "Driver", "id": "Driver"},
                            {"name": "S1 Time", "id": "Sector1"},
                            {"name": "Δ S1", "id": "DeltaS1"},
                            {"name": "S2 Time", "id": "Sector2"},
                            {"name": "Δ S2", "id": "DeltaS2"},
                            {"name": "S3 Time", "id": "Sector3"},
                            {"name": "Δ S3", "id": "DeltaS3"},
                        ],
                        style_cell={'textAlign': 'center', 'color': 'white', 'backgroundColor': '#222'},
                        style_header={'fontWeight': 'bold', 'backgroundColor': '#444', 'color': 'white'},
                        style_data_conditional=[
                            # Existing delta color rules
                            {
                                'if': {'column_id': 'DeltaS1', 'filter_query': '{DeltaS1} > 0'},
                                'color': 'red'
                            },
                            {
                                'if': {'column_id': 'DeltaS2', 'filter_query': '{DeltaS2} > 0'},
                                'color': 'red'
                            },
                            {
                                'if': {'column_id': 'DeltaS3', 'filter_query': '{DeltaS3} > 0'},
                                'color': 'red'
                            },
                            {
                                'if': {'column_id': 'DeltaS1', 'filter_query': '{DeltaS1} <= 0'},
                                'color': 'lime'
                            },
                            {
                                'if': {'column_id': 'DeltaS2', 'filter_query': '{DeltaS2} <= 0'},
                                'color': 'lime'
                            },
                            {
                                'if': {'column_id': 'DeltaS3', 'filter_query': '{DeltaS3} <= 0'},
                                'color': 'lime'
                            },

                            # New highlight for best sector times themselves:
                            {
                                'if': {'column_id': 'Sector1', 'filter_query': '{DeltaS1} = 0'},
                                'backgroundColor': '#28a745',  # Bootstrap success green
                                'color': 'white',
                                'fontWeight': 'bold',
                            },
                            {
                                'if': {'column_id': 'Sector2', 'filter_query': '{DeltaS2} = 0'},
                                'backgroundColor': '#28a745',
                                'color': 'white',
                                'fontWeight': 'bold',
                            },
                            {
                                'if': {'column_id': 'Sector3', 'filter_query': '{DeltaS3} = 0'},
                                'backgroundColor': '#28a745',
                                'color': 'white',
                                'fontWeight': 'bold',
                            },
                        ],
                        style_table={'overflowX': 'auto'},
                        page_size=10,
                    )
                ])
            ], color="dark", inverse=True, className="mb-4 shadow-sm"),
            width=12
        )
    ])
], fluid=True, className="bg-dark p-4")
