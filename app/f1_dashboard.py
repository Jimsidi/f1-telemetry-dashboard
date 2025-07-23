import os
import fastf1
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State

# Setup cache
os.makedirs('cache_dir', exist_ok=True)
fastf1.Cache.enable_cache('cache_dir')

app = Dash(__name__)
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

    html.Div(id='driver-select-container'),

    dcc.Graph(id='telemetry-plot')
])


# Callback to load session and show driver dropdown
@app.callback(
    Output('driver-select-container', 'children'),
    Input('load-button', 'n_clicks'),
    State('year-input', 'value'),
    State('round-input', 'value'),
    State('session-type', 'value')
)
def load_session(n_clicks, year, rnd, session_type):
    if n_clicks == 0:
        return ""

    try:
        session = fastf1.get_session(year, rnd, session_type.upper())
        session.load()
        drivers = session.laps['Driver'].unique()

        return html.Div([
            html.P(f"Loaded: {session.event['EventName']} - {session.name}"),
            html.Label("Select Drivers:"),
            dcc.Dropdown(
                options=[{"label": d, "value": d} for d in drivers],
                value=drivers[:2].tolist(),  # preselect first two
                multi=True,
                id='driver-dropdown'
            ),
            html.Div(id='session-store', style={'display': 'none'}, children=f"{year},{rnd},{session_type.upper()}")
        ])
    except Exception as e:
        return html.P(f"❌ Error loading session: {str(e)}")


# Callback to plot telemetry after driver selection
@app.callback(
    Output('telemetry-plot', 'figure'),
    Input('driver-dropdown', 'value'),
    State('session-store', 'children')
)
def update_plot(drivers, session_info):
    if not drivers or not session_info:
        return {}

    year, rnd, session_type = session_info.split(',')

    # Reload session
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

    # Get corner info
    try:
        corners_df = session.get_circuit_info().corners
        corner_distances = corners_df.set_index('Number').T.iloc[[4]].values.flatten()
    except:
        corner_distances = []

    fig = px.line(df, x="Distance", y="Speed", color="Driver",
                  title=f"Speed vs Distance - {session.event['EventName']} {year}")

    for cd in corner_distances:
        fig.add_vline(x=cd, line_dash="dash", line_color="gray", opacity=0.4)

    return fig


if __name__ == "__main__":
    app.run(debug=True)
