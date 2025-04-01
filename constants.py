import numpy as np
import redis
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import os

meta_variables = ['longitude', 'latitude', 'observation_depth', 'time', 'platform_type', 'platform_code', 'country']
surface_variables = ['sst','atmp','slp','windspd','winddir','clouds','dewpoint', 'hur', 'wvht', 'waterlevel_met_res', 'waterlevel_wrt_lcd', 'water_col_ht',]
unused_variables = ['uo','vo','wo','waterlevel','rainfall_rate', 'sea_water_elec_conductivity','sea_water_pressure','rlds','rsds','wind_to_direction']
depth_variables = ['ztmp','zsal']

long_names = {
    'sst':'Sea Surface Temperature',
    'atmp': 'Air Temperature',
    'slp': 'Sea Level Pressure',
    'windspd': 'Wind Speed',
    'winddir': 'Wind Direction',
    'clouds': 'Clouds',
    'dewpoint': "Dew Point Temperature",
    'ztmp': 'Temperature Profile',
    'zsal': 'Salinity',
    'hur': 'Relative Humidity', 
    'wvht': 'Wave Height', 
    'waterlevel_met_res': 'Meteorological Residual Tidal Elevation', 
    'waterlevel_wrt_lcd': 'Tidal Elevation WRT Local Chart Datum', 
    'water_col_ht': 'Water Column Height',
}

units = {
    'sst':'Deg C',
    'atmp': 'Deg C',
    'slp': 'hPa',
    'windspd': 'm/s',
    'winddir': 'Deg true',
    'clouds': 'oktas',
    'dewpoint': 'Deg C',
    'ztmp': 'Deg C',
    'zsal': 'PSU',
    'hur': '%', 
    'wvht': 'm', 
    'waterlevel_met_res': 'm', 
    'waterlevel_wrt_lcd': 'm', 
    'water_col_ht': 'm',
}

all_variables_comma_separated = ','.join(surface_variables) + ',' + ','.join(depth_variables) + ',' + ','.join(meta_variables)

dtypes = {
    'row': int,
    'platform_code': str,
    'platform_type': str,
    'country': str,
    'latitude': np.float64,
    'longitude': np.float64,
    'observation_depth': np.float64,
    'sst': np.float64,
    'atmp': np.float64,
    'ztmp': np.float64,
    'zsal': np.float64,
    'slp': np.float64,
    'windspd': np.float64,
    'winddir': np.float64,
    'clouds': np.float64,
    'dewpoint': np.float64,
    'longitude': np.float64, 
    'latitude': np.float64,
    'observation_depth': np.float64, 
    'platform_type': str, 
    'platform_code':str,
    'hur': np.float64, 
    'wvht': np.float64, 
    'waterlevel_met_res': np.float64, 
    'waterlevel_wrt_lcd': np.float64, 
    'water_col_ht': np.float64,
}

platforms = [
    'ARGO',
    'AUTONOMOUS PINNIPEDS',
    'C-MAN WEATHER STATIONS',
    'CLIMATE REFERENCE MOORED BUOYS',
    'DRIFTING BUOYS',
    'GLIDERS',
    'ICE BUOYS',
    'MOORED BUOYS',
    'RESEARCH',
    'SHIPS',
    'SHORE AND BOTTOM STATIONS',
    'TIDE GAUGE STATIONS',
    'TROPICAL MOORED BUOYS',
    'TSUNAMI WARNING STATIONS',
    'UNKNOWN',
    'UNMANNED SURFACE VEHICLE',
    'VOLUNTEER OBSERVING SHIPS',
    'VOSCLIM',
    'WEATHER AND OCEAN OBS',
    'WEATHER BUOYS',
    'WEATHER OBS'
]

# Define a redis instance. This definition will work both locally and with an app deployed to DE:
redis_instance = redis.StrictRedis.from_url(
    os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")
)

data_table = 'osmc'
counts_table = 'counts'
locations_table = 'locations'

# Create a SQLAlchemy connection string from the environment variable `DATABASE_URL`
# automatically created in your dash app when it is linked to a postgres container
# on Dash Enterprise. If you're running locally and `DATABASE_URL` is not defined,
# then this will fall back to a connection string for a local postgres instance
#  with username='postgres' and password='password'
connection_string = "postgresql" + os.environ.get(
    "DATABASE_URL", "postgresql+psycopg2://postgres:password@127.0.0.1:5432"
).lstrip("postgresql")

# Create a SQLAlchemy engine object. This object initiates a connection pool
# so we create it once here and import into app.py.
# `poolclass=NullPool` prevents the Engine from using any connection more than once. You'll find more info here:
# https://docs.sqlalchemy.org/en/14/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
postgres_engine = create_engine(connection_string, poolclass=NullPool,)

theme = {
    "accent":"#1f78b4",
    "accent_positive":"#017500",
    "accent_negative":"#C20000",
    "background_content":"#F9F9F9",
    "background_page":"#F2F2F2",
    "body_text":"#606060",
    "border":"#e2e2e2",
    "border_style":{
        "name":"underlined",
        "borderWidth":"0px 0px 1px 0px",
        "borderStyle":"solid",
        "borderRadius":0
    },
    "button_border":{
        "width":"1px",
        "color":"#1f78b4",
        "radius":"0px"
    },
    "button_capitalization":"uppercase",
    "button_text":"#1f78b4",
    "button_background_color":"#F9F9F9",
    "control_border":{
        "width":"0px 0px 1px 0px",
        "color":"#e2e2e2",
        "radius":"0px"
    },
    "control_background_color":"#F9F9F9",
    "control_text":"#606060",
    "card_margin":0,
    "card_padding":"5px",
    "card_border":{
        "width":"1px",
        "style":"solid",
        "color":"#e2e2e2",
        "radius":"0px"
    },
    "card_background_color":"#F9F9F9",
    "card_box_shadow":"0px 0px 0px rgba(0,0,0,0)",
    "card_outline":{
        "width":"1px",
        "style":"solid",
        "color":"#e2e2e2"
    },
    "card_header_accent":"#e2e2e2",
    "card_header_margin":"0px",
    "card_header_padding":"10px",
    "card_header_border":{
        "width":"0px 0px 1px 0px",
        "style":"solid",
        "color":"#e2e2e2",
        "radius":"0px"
    },
    "card_header_background_color":"#F9F9F9",
    "card_title_text":"#606060",
    "card_title_font_size":"20px",
    "card_description_background_color":"#FFF",
    "card_description_text":"#101010",
    "card_description_font_size":"16px",
    "card_menu_background_color":"#FFF",
    "card_menu_text":"#101010",
    "card_header_box_shadow":"0px 0px 0px rgba(0,0,0,0)",
    "card_accent":"#1f78b4",
    "breakpoint_font":"1200px",
    "breakpoint_stack_blocks":"700px",
    "colorway":[
        "#119dff",
        "#66c2a5",
        "#fc8d62",
        "#e78ac3",
        "#a6d854",
        "#ffd92f",
        "#e5c494",
        "#b3b3b3"
    ],
    "colorscale":[
        "#1f78b4",
        "#4786bc",
        "#6394c5",
        "#7ba3cd",
        "#92b1d5",
        "#a9c0de",
        "#bed0e6",
        "#d4dfee",
        "#eaeff7",
        "#ffffff"
    ],
    "dbc_primary":"#1f78b4",
    "dbc_secondary":"#7c7c7c",
    "dbc_info":"#009AC7",
    "dbc_gray":"#adb5bd",
    "dbc_success":"#017500",
    "dbc_warning":"#F9F871",
    "dbc_danger":"#C20000",
    "font_family":"Open Sans",
    "font_family_header":"Open Sans",
    "font_family_headings":"Open Sans",
    "font_size":"17px",
    "font_size_smaller_screen":"15px",
    "font_size_header":"24px",
    "footer_background_color":"#DDD",
    "footer_title_text":"#262626",
    "footer_title_font_size":"24px",
    "title_capitalization":"uppercase",
    "header_content_alignment":"spread",
    "header_margin":"0px",
    "header_padding":"0px",
    "header_border":{
        "width":"0px 0px 1px 0px",
        "style":"solid",
        "color":"#e2e2e2",
        "radius":"0px"
    },
    "header_background_color":"#F2F2F2",
    "header_box_shadow":"none",
    "header_text":"#606060",
    "heading_text":"#606060",
    "hero_background_color":"#F9F9F9",
    "hero_title_text":"#474747",
    "hero_title_font_size":"48px",
    "hero_subtitle_text":"#606060",
    "hero_subtitle_font_size":"16px",
    "hero_controls_background_color":"rgba(230, 230, 230, 0.90)",
    "hero_controls_label_text":"#464646",
    "hero_controls_label_font_size":"14px",
    "hero_controls_grid_columns":4,
    "hero_controls_accent":"#c1c1c1",
    "text":"#606060",
    "report_background":"#F2F2F2",
    "report_background_content":"#FAFBFC",
    "report_background_page":"white",
    "report_text":"black",
    "report_font_family":"Computer Modern",
    "report_font_size":"12px",
    "report_border":"#e2e2e2",
    "graph_grid_color":"#e2e2e2",
    "table_striped_even":"rgba(255,255,255,0)",
    "table_striped_odd":"rgba(0,0,0,0.05)",
    "table_border":"#e2e2e2",
    "tag_background_color":"#F1F1F1",
    "tag_text":"#474747",
    "tag_font_size":"14px",
    "tag_border":{
        "width":"1px",
        "style":"solid",
        "color":"#BEBEBE",
        "radius":"0px"
    },
    "tooltip_background_color":"#253247",
    "tooltip_text":"#FFF",
    "tooltip_font_size":"14px"
}