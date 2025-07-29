import os
import fastf1
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, Input, Output, State, html
import dash_bootstrap_components as dbc

# Setup cache
os.makedirs('cache_dir', exist_ok=True)
fastf1.Cache.enable_cache('cache_dir')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "F1 Telemetry Comparison"

# Layout
app.layout = dbc.Container([
    dbc.Card([
        dbc.CardBody([
            html.H1("🏎️ F1 Telemetry Lap Comparison", className="text-white"),
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
                    dbc.Label("Session Type (FP1, FP2, FP3, Q, S, R):", className="text-white"),
                    dbc.Input(id='session-type', type='text', value='Q'),
                ], width=3),
                dbc.Col([
                    html.Br(),
                    dbc.Button("Load Session", id='load-button', n_clicks=0, color='danger'),
                ], width=2),
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
    dbc.Card([
        dbc.CardBody([
            dcc.Graph(id='telemetry-plot'),
            dcc.Graph(id='track-map')
        ])
    ], color="light")
], fluid=True, className="bg-dark p-4")





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
    [Output('telemetry-plot', 'figure'),
     Output('track-map', 'figure')],
    [Input('driver-dropdown', 'value'),
     Input('telemetry-type', 'value')],
    State('session-store', 'children')
)
def update_plot(drivers, telemetry_type, session_info):
    if not drivers or not session_info:
        return {}, {}

    year, rnd, session_type = session_info.split(',')

    session = fastf1.get_session(int(year), int(rnd), session_type)
    session.load()

    # --- Telemetry plot (speed, throttle, etc.) ---
    all_tel = []
    for driver in drivers:
        try:
            lap = session.laps.pick_drivers(driver).pick_fastest()
            tel = lap.get_car_data().add_distance()
            tel['Driver'] = driver
            all_tel.append(tel)
        except Exception as e:
            print(f"Error getting telemetry for {driver}: {e}")

    if all_tel:
        df = pd.concat(all_tel)
        fig1 = px.line(df, x='Distance', y=telemetry_type, color='Driver',
                       title=f"{telemetry_type} vs Distance - {session.event['EventName']} {year}")
        # Add corner markers to telemetry plot
        try:
            corners_df = session.get_circuit_info().corners
            corner_distances = corners_df.set_index('Number').T.iloc[[4]].values.flatten()
            for cd in corner_distances:
                fig1.add_vline(x=cd, line_dash="dash", line_color="gray", opacity=0.4)
        except Exception as e:
            print(f"Error adding corner markers: {e}")
    else:
        fig1 = {}

    # --- Track map plot ---
    fig2 = go.Figure()
    for driver in drivers:
        try:
            lap = session.laps.pick_drivers(driver).pick_fastest()
            tel = lap.get_telemetry()
            fig2.add_trace(go.Scatter(
                x=tel['X'],
                y=tel['Y'],
                mode='lines',
                name=driver,
                line=dict(width=3),
                text=[f"{telemetry_type}: {val:.2f}" for val in tel[telemetry_type]],
                hoverinfo="text+name"
            ))
        except Exception as e:
            print(f"Track map error for {driver}: {e}")

    # Add turn labels
    try:
        corners = session.get_circuit_info().corners
        for _, row in corners.iterrows():
            fig2.add_annotation(
                x=row['X'],
                y=row['Y'],
                text=f"Turn {int(row['Number'])}",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-20,
                font=dict(size=10, color="black"),
                bgcolor="rgba(255,255,255,0.7)",
                bordercolor="black",
                borderwidth=1
            )
    except Exception as e:
        print(f"Error adding turn labels: {e}")

    fig2.update_layout(
        title=f"Track Map - Driver Paths",
        xaxis_title="X",
        yaxis_title="Y",
        yaxis_scaleanchor="x",
        width = 1100,
        height = 900,
        showlegend=True
    )

    return fig1, fig2

if __name__ == "__main__":
    app.run(debug=True)
