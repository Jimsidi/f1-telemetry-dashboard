import os
from dash import Dash
import dash_bootstrap_components as dbc

os.makedirs("app/cache_dir", exist_ok=True)

import fastf1
fastf1.Cache.enable_cache("app/cache_dir")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "F1 Telemetry Comparison"

from .layout import layout
from .callbacks import register_callbacks

app.layout = layout
register_callbacks(app)
