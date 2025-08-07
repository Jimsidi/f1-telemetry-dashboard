from dash import Input, Output, State, MATCH
import fastf1
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def register_callbacks(app):
    @app.callback(
        [
            Output('driver-dropdown', 'options'),
            Output('driver-dropdown', 'value'),
            Output('driver-dropdown', 'style'),
            Output('driver-label', 'style'),
            Output('telemetry-type', 'style'),
            Output('telemetry-label', 'style'),
            Output('session-store', 'children'),
            Output('lap-dropdown', 'options'),
            Output('lap-dropdown', 'value'),
            Output('lap-dropdown', 'style'),
            Output('lap-label', 'style'),
            Output('lap-delta-table', 'data'),
        ],
        Input('load-button', 'n_clicks'),
        State('year-input', 'value'),
        State('round-input', 'value'),
        State('session-type', 'value'),
    )
    def load_session(n_clicks, year, rnd, session_type):
        hidden_style = {'display': 'none'}
        visible_style = {'display': 'block'}

        if n_clicks == 0:
            return [], [], hidden_style, hidden_style, hidden_style, hidden_style, "", [], [], hidden_style, hidden_style, []

        try:
            session = fastf1.get_session(year, rnd, session_type.upper())
            session.load()
            drivers = session.laps['Driver'].unique()

            options = [{"label": d, "value": d} for d in drivers]
            preselected = drivers[:2].tolist()

            # Lap selection
            lap_numbers = session.laps['LapNumber'].unique()
            lap_options = [{'label': f"Lap {int(lap)}", 'value': int(lap)} for lap in lap_numbers]
            default_laps = [int(lap) for lap in lap_numbers[:2]]

            session_info = f"{year},{rnd},{session_type.upper()}"

            # Lap Delta Table
            try:
                fastest_laps = session.laps.pick_quicklaps().copy()
                fastest_laps['LapTime'] = pd.to_timedelta(fastest_laps['LapTime'])

                fastest_laps['LapTimeSeconds'] = fastest_laps['LapTime'].apply(lambda x: x.total_seconds())
                fastest_laps = fastest_laps.sort_values('LapTimeSeconds')
                best_time = fastest_laps.iloc[0]['LapTimeSeconds']
                fastest_laps['Delta'] = fastest_laps['LapTimeSeconds'] - best_time

                def format_laptime(td):
                    total = td.total_seconds()
                    minutes = int(total // 60)
                    seconds = total % 60
                    return f"{minutes}:{seconds:05.2f}"

                fastest_laps['LapTimeStr'] = fastest_laps['LapTime'].apply(format_laptime)

                #Compound column to final dict
                lap_delta_data = fastest_laps[['Driver', 'LapTimeStr', 'Delta', 'Compound']].rename(
                    columns={'LapTimeStr': 'LapTime'}
                ).to_dict('records')

            except Exception as e:
                print(f"Lap delta build error: {e}")
                lap_delta_data = []

            return (
                options, preselected, visible_style, visible_style,
                visible_style, visible_style, session_info,
                lap_options, default_laps, visible_style, visible_style,
                lap_delta_data
            )

        except Exception as e:
            print(f"Error loading session: {e}")
            return [], [], hidden_style, hidden_style, hidden_style, hidden_style, "", [], [], hidden_style, hidden_style, []

    # Callback to plot telemetry after driver selection
    @app.callback(
        [Output('telemetry-plot', 'figure'),
         Output('track-map', 'figure'),
         Output('weather-plot', 'figure'),
         Output('sector-comparison-chart', 'figure'),
         Output('sector-comparison-table', 'data')],
        [Input('driver-dropdown', 'value'),
         Input('telemetry-type', 'value'),
         Input('lap-dropdown', 'value')],
        State('session-store', 'children')
    )
    def update_plot(drivers, telemetry_type, laps, session_info):
        if not drivers or not laps or not session_info:
            return {}, {}, {}, {}, []

        year, rnd, session_type = session_info.split(',')
        session = fastf1.get_session(int(year), int(rnd), session_type)
        session.load()
        all_tel = []
        for driver in drivers:
            for lap_num in laps:
                try:
                    lap = session.laps.pick_drivers(driver).pick_laps(int(lap_num))
                    tel = lap.get_car_data().add_distance()
                    tel['Driver'] = driver
                    tel['Lap'] = f"Lap {lap_num}"
                    all_tel.append(tel)
                except Exception as e:
                    print(f"Error getting telemetry for {driver} lap {lap_num}: {e}")

        if all_tel:
            df = pd.concat(all_tel)
            fig1 = px.line(df, x='Distance', y=telemetry_type, color='Lap',
                           line_dash='Driver' if len(drivers) > 1 else None,
                           title=f"{telemetry_type} vs Distance")
        else:
            fig1 = {}

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

            # Turn labels
            try:
                corners = session.get_circuit_info().corners
                for i, (_, row) in enumerate(corners.iterrows()):
                    offset = 20 if i % 2 == 0 else -20  # Zigzag vertical position

                    fig2.add_annotation(
                        x=row['X'],
                        y=row['Y'],
                        text=f"Turn{int(row['Number'])}",
                        showarrow=True,
                        arrowhead=1,
                        arrowsize=1,
                        ax=20 if i % 2 == 0 else -20,
                        ay=offset,
                        font=dict(size=9, color="black"),
                        bgcolor="rgba(255,255,255,0.6)",
                        bordercolor="black",
                        borderwidth=1.5,
                        opacity=0.5
                    )
            except Exception as e:
                print(f"Error adding turn labels: {e}")

        fig2.update_layout(
            title="Track Map - Fastest Laps Only",
            xaxis_title="X",
            yaxis_title="Y",
            yaxis_scaleanchor="x",
            width=1100,
            height=900,
            showlegend=True
        )

        # --- Weather plot ---
        try:
            weather_df = session.weather_data
            weather_fig = px.line(weather_df, x='Time', y=['AirTemp', 'TrackTemp'],
                                  labels={'value': 'Temperature (°C)', 'Time': 'Session Time'},
                                  title="Air vs Track Temperature Over Time")
        except Exception as e:
            print(f"Weather plot error: {e}")
            weather_fig = {}

        # --- Sector Comparison ---
        try:
            sector_data = []

            for driver in drivers:
                lap = session.laps.pick_drivers(driver).pick_fastest()
                s1 = lap['Sector1Time'].total_seconds()
                s2 = lap['Sector2Time'].total_seconds()
                s3 = lap['Sector3Time'].total_seconds()
                sector_data.append({
                    "Driver": driver,
                    "Sector 1": s1,
                    "Sector 2": s2,
                    "Sector 3": s3
                })

            df_sectors = pd.DataFrame(sector_data)

            sector_fig = px.bar(
                df_sectors,
                x='Driver',
                y=['Sector 1', 'Sector 2', 'Sector 3'],
                title="Sector Time Comparison (s)",
                labels={"value": "Time (s)", "variable": "Sector"},
                barmode="stack"
            )

            sector_fig.update_layout(legend_title_text='Sector')
        except Exception as e:
            print(f"Sector comparison error: {e}")
            sector_fig = {}

        # --- Sector Comparison Table ---
        try:
            sector_data = session.laps.pick_quicklaps().copy()
            sector_data['Sector1Time'] = pd.to_timedelta(sector_data['Sector1Time'])
            sector_data['Sector2Time'] = pd.to_timedelta(sector_data['Sector2Time'])
            sector_data['Sector3Time'] = pd.to_timedelta(sector_data['Sector3Time'])

            # Make an explicit copy here to avoid SettingWithCopyWarning
            sector_data = sector_data[sector_data['Driver'].isin(drivers)].copy()

            sector_data['Sector1Sec'] = sector_data['Sector1Time'].apply(lambda x: x.total_seconds())
            sector_data['Sector2Sec'] = sector_data['Sector2Time'].apply(lambda x: x.total_seconds())
            sector_data['Sector3Sec'] = sector_data['Sector3Time'].apply(lambda x: x.total_seconds())

            # Get best per sector
            best_s1 = sector_data['Sector1Sec'].min()
            best_s2 = sector_data['Sector2Sec'].min()
            best_s3 = sector_data['Sector3Sec'].min()

            def fmt(td):  # Format timedelta
                sec = td.total_seconds()
                return f"{int(sec // 60)}:{sec % 60:05.2f}"

            sector_table = []
            for _, row in sector_data.iterrows():
                sector_table.append({
                    'Driver': row['Driver'],
                    'Sector1': fmt(row['Sector1Time']),
                    'DeltaS1': round(row['Sector1Sec'] - best_s1, 3),
                    'BestS1': row['Sector1Sec'] == best_s1,  # Flag for best sector 1
                    'Sector2': fmt(row['Sector2Time']),
                    'DeltaS2': round(row['Sector2Sec'] - best_s2, 3),
                    'BestS2': row['Sector2Sec'] == best_s2,
                    'Sector3': fmt(row['Sector3Time']),
                    'DeltaS3': round(row['Sector3Sec'] - best_s3, 3),
                    'BestS3': row['Sector3Sec'] == best_s3,
                })

        except Exception as e:
            print(f"Error building sector table: {e}")
            sector_table = []

        return fig1, fig2, weather_fig, sector_fig, sector_table

    @app.callback(
        Output({"type": "collapse-body", "section": MATCH}, "is_open"),
        Input({"type": "collapse-toggle", "section": MATCH}, "n_clicks"),
        State({"type": "collapse-body", "section": MATCH}, "is_open"),
        prevent_initial_call=True
    )
    def toggle_collapse(n, is_open):
        return not is_open


