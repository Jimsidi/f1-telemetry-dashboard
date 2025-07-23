import os
import fastf1
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State

# Setup cache
os.makedirs('cache_dir', exist_ok=True)
fastf1.Cache.enable_cache('cache_dir')

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "F1 Telemetry Comparison"

# Layout
app.layout = html.Div([
    html.H1("F1 Telemetry Lap Comparison"),

    html.Div([
        html.Label("Year:"),
        dcc.Input(id='year-input', type='number', value=2024, min=2018, max=2025),

        html.Label("Round:"),
        dcc.Input(id='round-input', type='number', value=17, min=1, max=25),

        html.Label("Session Type (FP1, FP2, FP3, Q, S, R):"),
        dcc.Input(id='session-type', type='text', value='Q'),

        html.Button("Load Session", id='load-button', n_clicks=0),
    ], style={'margin-bottom': '20px'}),

    # Placeholders, initially empty/hidden
    html.Div([
        html.Label("Select Drivers:", id='driver-label', style={'display': 'none'}),
        dcc.Dropdown(id='driver-dropdown', multi=True, options=[], value=[], style={'display': 'none'}),
    ], style={'margin-bottom': '20px'}),

    html.Div([
        html.Label("Select Telemetry Channel:", id='telemetry-label', style={'display': 'none'}),
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
            style={'width': '200px', 'display': 'none'}
        ),
    ], style={'margin-bottom': '20px'}),

    # Hidden div to store session info
    html.Div(id='session-store', style={'display': 'none'}, children=""),

    dcc.Graph(id='telemetry-plot')
])




# Callback to load session and show driver dropdown
@app.callback(
    [
        Output('driver-dropdown', 'options'),
        Output('driver-dropdown', 'value'),
        Output('driver-dropdown', 'style'),
        Output('driver-label', 'style'),
        Output('telemetry-type', 'style'),
        Output('telemetry-label', 'style'),
        Output('session-store', 'children'),
    ],
    Input('load-button', 'n_clicks'),
    State('year-input', 'value'),
    State('round-input', 'value'),
    State('session-type', 'value'),
)
def load_session(n_clicks, year, rnd, session_type):
    if n_clicks == 0:
        # Hide everything initially
        hidden_style = {'display': 'none'}
        return [], [], hidden_style, hidden_style, hidden_style, hidden_style, ""

    try:
        session = fastf1.get_session(year, rnd, session_type.upper())
        session.load()
        drivers = session.laps['Driver'].unique()

        options = [{"label": d, "value": d} for d in drivers]
        preselected = drivers[:2].tolist()

        # Show dropdowns and labels
        visible_style = {'display': 'block'}

        session_info = f"{year},{rnd},{session_type.upper()}"

        return options, preselected, visible_style, visible_style, visible_style, visible_style, session_info

    except Exception as e:
        # On error, hide dropdowns and clear session info
        hidden_style = {'display': 'none'}
        return [], [], hidden_style, hidden_style, hidden_style, hidden_style, ""




# Callback to plot telemetry after driver selection
@app.callback(
    Output('telemetry-plot', 'figure'),
    [Input('driver-dropdown', 'value'),
     Input('telemetry-type', 'value')],
    State('session-store', 'children')
)
def update_plot(drivers, telemetry_type, session_info):
    if not drivers or not session_info:
        return {}

    year, rnd, session_type = session_info.split(',')

    session = fastf1.get_session(int(year), int(rnd), session_type)
    session.load()

    all_tel = []
    for driver in drivers:
        try:
            lap = session.laps.pick_drivers(driver).pick_fastest()
            tel = lap.get_car_data().add_distance()
            tel['Driver'] = driver
            all_tel.append(tel)
        except Exception as e:
            print(f"Error getting data for {driver}: {e}")

    df = pd.concat(all_tel)

    fig = px.line(df, x='Distance', y=telemetry_type, color='Driver',
                  title=f"{telemetry_type} vs Distance - {session.event['EventName']} {year}")

    # Optional: add corner markers here

    return fig



if __name__ == "__main__":
    app.run(debug=True)
