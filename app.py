from dash import Dash, dcc, html, Input, Output, State, exceptions, ctx
import dash_design_kit as ddk
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import flask
import urllib
import pandas as pd
import numpy as np
import zc
import constants
import db
import colorcet as cc

import json
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

cones_url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/osmc_cones.csv?latitude,longitude,name,index,time&orderBy("name,index")'
data_url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/osmc_rt_60'

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server = app.server  # expose server variable for Procfile

with open('key.txt') as key:
    ESRI_API_KEY = key.readline()

center = {'lon': 0.0, 'lat': 0.0}
zoom = 1.4

height_of_row=345
header_footer_fudge = 150
map_height = 520

def cc_color_set(index, palette):
    rgb = px.colors.convert_to_RGB_255(palette[index])
    hexi = '#%02x%02x%02x' % rgb
    return hexi

def cc_color_set_transparent(index, palette, alpha):
    h = palette[index].lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    color = 'rgba(' + str(rgb[0]) + ',' + str(rgb[1]) + ',' + str(rgb[2]) + ',' + str(alpha) + ')'
    return color
    

platform_color = {
    'ARGO' : cc_color_set(0, cc.glasbey_bw_minc_20),
    'AUTONOMOUS PINNIPEDS': cc_color_set(1, cc.glasbey_bw_minc_20),
    'C-MAN WEATHER STATIONS': cc_color_set(2, cc.glasbey_bw_minc_20), 
    'CLIMATE REFERENCE MOORED BUOYS': cc_color_set(3, cc.glasbey_bw_minc_20), 
    'DRIFTING BUOYS': cc_color_set(4, cc.glasbey_bw_minc_20), 
    'GLIDERS': cc_color_set(5, cc.glasbey_bw_minc_20),
    'ICE BUOYS': cc_color_set(6, cc.glasbey_bw_minc_20),
    'MOORED BUOYS': cc_color_set(7, cc.glasbey_bw_minc_20),
    'RESEARCH': cc_color_set(8, cc.glasbey_bw_minc_20),
    'SHIPS': cc_color_set(9, cc.glasbey_bw_minc_20),
    'SHORE AND BOTTOM STATIONS': cc_color_set(10, cc.glasbey_bw_minc_20),
    'TIDE GAUGE STATIONS': cc_color_set(11, cc.glasbey_bw_minc_20),
    'TROPICAL MOORED BUOYS': cc_color_set(12, cc.glasbey_bw_minc_20),
    'TSUNAMI WARNING STATIONS': cc_color_set(13, cc.glasbey_bw_minc_20),
    'UNKNOWN': cc_color_set(14, cc.glasbey_bw_minc_20),
    'UNCREWED SURFACE VEHICLE': cc_color_set(15, cc.glasbey_bw_minc_20),
    'VOLUNTEER OBSERVING SHIPS': cc_color_set(16, cc.glasbey_bw_minc_20),
    'VOSCLIM': cc_color_set(17, cc.glasbey_bw_minc_20),
    'WEATHER AND OCEAN OBS': cc_color_set(18, cc.glasbey_bw_minc_20),
    'WEATHER BUOYS': cc_color_set(19, cc.glasbey_bw_minc_20),
    'WEATHER OBS': cc_color_set(20, cc.glasbey_bw_minc_20),
}

# platform_color = {
#     'ARGO' : '#0040FF',
#     'AUTONOMOUS PINNIPEDS': '#FF0000',
#     'C-MAN WEATHER STATIONS': '#FF7F00', 
#     'CLIMATE REFERENCE MOORED BUOYS': '#FFD400', 
#     'DRIFTING BUOYS': '#FFFF00', 
#     'GLIDERS': '#BFFF00',
#     'ICE BUOYS': '#6AFF00',
#     'MOORED BUOYS': '#00EAFF',
#     'RESEARCH': '#AA00FF',
#     'SHIPS': '#FF00AA',
#     'SHORE AND BOTTOM STATIONS': '#EDB9B9',
#     'TIDE GAUGE STATIONS': '#E7E9B9',
#     'TROPICAL MOORED BUOYS': '#B9EDE0',
#     'TSUNAMI WARNING STATIONS': '#B9D7ED',
#     'UNKNOWN': '#DCB9ED',
#     'UNMANNED SURFACE VEHICLE': '#8F2323',
#     'VOLUNTEER OBSERVING SHIPS': '#8F6A23',
#     'VOSCLIM': '#23628F',
#     'WEATHER AND OCEAN OBS': '#6B238F',
#     'WEATHER BUOYS': '#000000',
#     'WEATHER OBS': '#737373',
# }

country_color = {
    'AUSTRALIA' : cc_color_set(21, cc.glasbey_bw_minc_20),
    'BENIN' : cc_color_set(22, cc.glasbey_bw_minc_20),
    'BRAZIL' : cc_color_set(23, cc.glasbey_bw_minc_20),
    'BULGARIA' : cc_color_set(24, cc.glasbey_bw_minc_20),
    'CANADA' : cc_color_set(25, cc.glasbey_bw_minc_20),
    'CHINA' : cc_color_set(26, cc.glasbey_bw_minc_20),
    'CROATIA' : cc_color_set(27, cc.glasbey_bw_minc_20),
    'EL SALVADOR' : cc_color_set(28, cc.glasbey_bw_minc_20),
    'EUROPEAN UNION' : cc_color_set(29, cc.glasbey_bw_minc_20),
    'FRANCE' : cc_color_set(30, cc.glasbey_bw_minc_20),
    'GERMANY' : cc_color_set(31, cc.glasbey_bw_minc_20),
    'GREECE' : cc_color_set(32, cc.glasbey_bw_minc_20),
    'HONG KONG' : cc_color_set(33, cc.glasbey_bw_minc_20),
    'INDIA' : cc_color_set(34, cc.glasbey_bw_minc_20),
    'IRAN, ISLAMIC REPUBLIC OF' : cc_color_set(35, cc.glasbey_bw_minc_20),
    'IRELAND' : cc_color_set(36, cc.glasbey_bw_minc_20),
    'ISRAEL' : cc_color_set(37, cc.glasbey_bw_minc_20),
    'ITALY' : cc_color_set(38, cc.glasbey_bw_minc_20),
    'JAPAN' : cc_color_set(39, cc.glasbey_bw_minc_20),
    'KOREA, REPUBLIC OF' : cc_color_set(40, cc.glasbey_bw_minc_20),
    'NETHERLANDS' : cc_color_set(41, cc.glasbey_bw_minc_20),
    'NEW ZEALAND' : cc_color_set(42, cc.glasbey_bw_minc_20),
    'NORWAY' : cc_color_set(43, cc.glasbey_bw_minc_20),
    'PHILIPPINES' : cc_color_set(44, cc.glasbey_bw_minc_20),
    'POLAND' : cc_color_set(45, cc.glasbey_bw_minc_20),
    'PORTUGAL' : cc_color_set(46, cc.glasbey_bw_minc_20),
    'ROMANIA' : cc_color_set(47, cc.glasbey_bw_minc_20),
    'RUSSIAN FEDERATION' : cc_color_set(48, cc.glasbey_bw_minc_20),
    'SOUTH AFRICA' : cc_color_set(49, cc.glasbey_bw_minc_20),
    'SPAIN' : cc_color_set(50, cc.glasbey_bw_minc_20),
    'SYRIAN ARAB REPUBLIC' : cc_color_set(51, cc.glasbey_bw_minc_20),
    'UNITED KINGDOM' : cc_color_set(52, cc.glasbey_bw_minc_20),
    'UNITED STATES' : cc_color_set(53, cc.glasbey_bw_minc_20),
    'UNKNOWN' : cc_color_set(54, cc.glasbey_bw_minc_20),
}

test_file = 'data/nc_osmc_data_rt_test.csv'

options_from_OSMC_LAS=[
    {'value':'ID' , 'label':'All Parameters'},
    { 'value':'SST','label': 'Sea Surface Temperature'},
    { 'value':'SSS','label': 'Sea Surface Salinity'},
    { 'value':'ZTMP','label': 'Temperature Profile'},
    { 'value':'SLP','label': 'Sea Level Pressure'},
    { 'value':'ATMP','label': 'Air Temperature'},
    { 'value':'ZSAL','label': 'Salinity'},
    { 'value':'WINDSPD','label': 'Wind Speed'},
    { 'value':'WINDDIR','label': 'Wind Direction'},
    { 'value':'CLOUDS','label': 'Clouds'},
    { 'value':'PRECIP','label': 'Precipitation'},
    { 'value':'WVHT','label': 'Wave Height'},
    { 'value':'FCO2W','label':'Fugacity of CO2 in Seawater'},
    { 'value':'WATER_COL_HT','label': 'Water Column Height'},
    { 'value':'WATERLEVEL_WRT_LCD','label': 'Tidal Elevation WRT local chart datum'},
    { 'value':'WATERLEVEL_MET_RES','label': 'Meteorological Residual Tidal Elevation'}
]

no_data_graph = go.Figure()
no_data_graph = no_data_graph.update_layout(
    xaxis =  { "visible": False },
    yaxis = { "visible": False },
    annotations = [
        {   
            "text": "No data found for selected platform...",
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {
                "size": 28
            }
        }
    ]
)

select_graph = go.Figure()
select_graph = select_graph.update_layout(
    xaxis =  { "visible": False },
    yaxis = { "visible": False },
    annotations = [
        {   
            "text": "Select a platform from the map or menu...",
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {
                "size": 28
            }
        }
    ]
)

app.layout = ddk.App([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='trigger', n_intervals=0, 
    max_intervals=0, #<-- only run once
    interval=1),
    dcc.Store(id='map-info'),
    dcc.Store(id='ui-state'),
    dcc.Store(id='download-url'),
    ddk.Header([
        ddk.Logo(src=app.get_asset_url('noaa-logo-rgb-2022.png'), style={'height':'90px'}),
        ddk.Title('Observing System Monitoring Center'),
        dcc.Loading(html.Div(id='map-loader', style={'float': 'right', 'display': 'none'}))
    ]),
    ddk.Block (id='control-block', width=20, children=[
        ddk.Card(
            children=[
                ddk.Row(ddk.Title('Country:', style={'font-size':'.8em', 'padding-left':'5px'})),
                dcc.Dropdown(
                    id='country',
                    clearable=True,
                    multi=True,
                    style={'padding-left': '10px'},
                    options=[],
                ),
                ddk.Row(ddk.Title('Parameter:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.Dropdown(
                    id='variable',
                    clearable=True,
                    multi=True,
                    style={'padding-left': '10px'},
                    options=[],
                ),
                ddk.Row(ddk.Title('Platform Type:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.Dropdown(
                    id='platform-type',
                    clearable=True,
                    multi=True,
                    style={'padding-left': '10px'},
                    options=[]
                ),
                ddk.Row(ddk.Title('Color Markers by:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.RadioItems(
                    id='color-by',
                    options=[],
                ),
                ddk.Row(ddk.Title('Find Platforms:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.Dropdown(
                    id='platform-code',
                    clearable=True,
                    multi=False,
                    style={'padding-left': '10px'},
                ),
                html.Hr(style={'border': '1px solid black'}),
                ddk.Row(ddk.Title('Plot Options:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.Dropdown(
                    id='markers',
                    options=[
                        {'label': 'Both lines and markers', 'value': 'both'},
                        {'label': 'Markers only', 'value': 'markers'},
                        {'label': 'Lines only', 'value': 'lines'}
                    ],
                    value='both',   
                ),
                html.Hr(style={'border': '1px solid black'}),
                ddk.Row(dcc.Loading(html.A(html.Button(id='download-button', children=['Download'], style={'font-size':'.8em', 'padding-left': '5px'},), target='_blank', id='download-link'))),
                dcc.Dropdown(
                    style={'margin-right': '5px'},
                    id='download-format',
                    options=[
                        {'label': 'CSV', 'value': '.csv'},
                        {'label': 'netCDF', 'value': '.ncCF'},
                        {'label': 'HTML', 'value': '.htmlTable'}
                    ],
                    placeholder='Select Download Format',   
                )
            ]
        )
    ]),
    ddk.Block(width=80, children=[
        ddk.Card(id='map-card', children=[
            ddk.CardHeader(id='map-card-header', 
                           modal=True, 
                           modal_config={'height': 90, 'width': 95}, 
                           fullscreen=True
                           ),
            dcc.Graph(id='location-map', style={'padding-left': '20px'}),
        ]),
    ]),
    ddk.Block(width=100, children=[
        ddk.Card(width=100, children=[
            ddk.CardHeader(id='plots-header', 
                title='Plots...',
                modal=True, 
                modal_config={'height': 90, 'width': 95}, 
                fullscreen=True,
            ),
            dcc.Loading(dcc.Graph(id='plots', style={'padding-left': '20px'})),
        ])
    ]),
])


##
# This runs on-load and builds the control and sets the options and values of the controls based on the state of the URL
@app.callback([
    Output('control-block', 'children'),
    Output('markers', 'value'),
],[
    Input('trigger', 'n_intervals'),
]
)
def read_url(trigger):
    out_platform_code = None
    out_line_marker_setting = 'both'
    out_platform_type = None
    out_color_by = 'platform_type'
    out_variable = None
    out_country = None
    
    url = flask.request.referrer
    parts = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parts.query)

    if 'markers' in params:
        line_plot_markers = params['markers'][0]
    
    if 'platform_code' in params:
        out_platform_code = params['platform_code'][0]

    if 'platform_type' in params:
        out_platform_type = params['platform_type']
    
    if 'color_by' in params:
        out_color_by = params['color_by'][0]
    
    if 'variable' in params:
        out_variable = params['variable']
    
    if 'country' in params:
        out_country = params['country']

    map_df = db.get_locations()
    counts_df = db.get_counts()
    if out_variable is not None:
        query = ""
        if isinstance(out_variable, list):
            if len(out_variable) > 0:
                for qidx, qvar in enumerate(out_variable):
                    if qidx == 0:
                        query = query + qvar + '> 0'
                    else:
                        query = query + ' or ' + qvar + '> 0'
        elif isinstance(out_variable, str):
            query = query + out_variable + '> 0'
        if len(query) > 1:
            has_data = counts_df.query(query)
            map_df = map_df[map_df['platform_code'].isin(has_data['platform_code'])]

    if out_platform_type is not None:
        if isinstance(out_platform_type, str):
            map_df = map_df.loc[map_df['platform_type'] == out_platform_type]
        elif isinstance(out_platform_type, list):
            query = ''
            for pi, plat in enumerate(out_platform_type):
                if pi == 0:
                    query = query  + 'platform_type==\''+plat+'\''
                else:
                    query = query  + 'or platform_type==\''+plat+'\''
            if len(query) > 1:
                map_df = map_df.query(query)
    
    if out_country is not None:
        if isinstance(out_country, str):
            map_df = map_df.loc[map_df['country'] == out_country]
        elif isinstance(out_country, list):
            query = ''
            for ci, cntry in enumerate(out_country):
                if ci == 0:
                    query = query  + 'country==\''+cntry+'\''
                else:
                    query = query  + 'or country==\''+cntry+'\''
            if len(query) > 1:
                map_df = map_df.query(query)
    
    codes_to_show = pd.unique(map_df['platform_code'])
    platform_code_options = []
    codes_to_show.sort()
    for codey in codes_to_show:
       platform_code_options.append({'label': codey, 'value': codey})

    control_block = [
        ddk.Card(
            children=[
                ddk.Row(ddk.Title('Country:', style={'font-size':'.8em', 'padding-left':'5px'})),
                dcc.Dropdown(
                    id='country',
                    clearable=True,
                    multi=True,
                    style={'padding-left': '10px'},
                    options=[
                        {'value': "AUSTRALIA", 'label': 'Australia'},
                        {'value': 'BENIN', 'label': 'Benin'},
                        {'value': "BRAZIL", 'label': 'Brazil'},
                        {'value': 'BULGARIA', 'label': 'Bulgaria'},
                        {'value': "CANADA", 'label': 'Canada'},
                        {'value': "CHINA", 'label': 'China'},
                        {'value': 'CROATIA', 'label': 'Croatia'},
                        {'value': 'EL SALVADOR', 'label': 'El Salvador'},
                        {'value': "EUROPEAN UNION", 'label': 'European Union'},
                        {'value': "FRANCE", 'label': 'France'},
                        {'value': "GERMANY", 'label': 'Germany'},
                        {'value': 'GREECE', 'label' : 'Greece'},
                        {'value': 'HONG KONG', 'label': 'Hong Kong'},
                        {'value': "INDIA", 'label': 'India'},
                        {'value': 'IRAN, ISLAMIC REPUBLIC OF', 'label' : 'Iran, Islamic Republic of'},
                        {'value': "IRELAND", 'label': 'Ireland'},
                        {'value': 'ISRAEL', 'label': 'Israel'},
                        {'value': 'ITALY', 'label': 'Italy'},
                        {'value': "JAPAN", 'label': 'Japan'},
                        {'value': "KOREA, REPUBLIC OF", 'label': 'South Korea'},
                        {'value': 'NETHERLANDS', 'label' : 'Netherlands'},
                        {'value': 'NEW ZEALAND', 'label' : 'New Zealand'},
                        {'value': 'NORWAY', 'label' : 'Norway'},
                        {'value': 'PHILIPPINES', 'label' : 'Philippines'},
                        {'value': 'POLAND', 'label' : 'Poland'},
                        {'value': 'PORTUGAL', 'label' : 'Portugal'},
                        {'value': 'ROMANIA', 'label' : 'Romania'},
                        {'value': 'RUSSIAN FEDERATION', 'label' : 'Russian Federation'},
                        {'value': "SPAIN", 'label': 'Spain'},
                        {'value': "SOUTH AFRICA", 'label': 'South Africa'},
                        {'value': 'SYRIAN ARAB REPUBLIC', 'label' : 'Syrian Arab Republic'},
                        {'value': "UKRAINE", 'label': 'Ukraine'},
                        {'value': "UNITED KINGDOM", 'label': 'United Kingdom'},
                        {'value': "UNITED STATES", 'label': 'United States'},
                        {'value': 'UNKNOWN', 'label': 'Unknown'},
                    ],
                    value=out_country
                ),
                ddk.Row(ddk.Title('Parameter:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.Dropdown(
                    id='variable',
                    clearable=True,
                    multi=True,
                    style={'padding-left': '10px'},
                    options=[
                        {'value':'sst','label': 'Sea Surface Temperature'},
                        {'value':'ztmp','label': 'Temperature Profile'},
                        {'value':'slp','label': 'Sea Level Pressure'},
                        {'value':'atmp','label': 'Air Temperature'},
                        {'value':'zsal','label': 'Salinity'},
                        {'value':'windspd','label': 'Wind Speed'},
                        {'value':'winddir','label': 'Wind Direction'},
                        {'value':'clouds','label': 'Clouds'},
                    ],
                    value=out_variable
                ),
                ddk.Row(ddk.Title('Platform Type:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.Dropdown(
                    id='platform-type',
                    clearable=True,
                    multi=True,
                    style={'padding-left': '10px'},
                    value=out_platform_type,
                    options=[
                        {'label': 'ARGO', 'value': 'ARGO'},
                        {'label': 'AUTONOMOUS PINNIPEDS', 'value': 'AUTONOMOUS PINNIPEDS'},
                        {'label': 'C-MAN WEATHER STATIONS', 'value': 'C-MAN WEATHER STATIONS'},
                        {'label': 'CLIMATE REFERENCE MOORED BUOYS', 'value': 'CLIMATE REFERENCE MOORED BUOYS'},
                        {'label': 'DRIFTING BUOYS', 'value': 'DRIFTING BUOYS'},
                        {'label': 'GLIDERS', 'value': 'GLIDERS'},
                        {'label': 'ICE BUOYS', 'value': 'ICE BUOYS'},
                        {'label': 'MOORED BUOYS', 'value': 'MOORED BUOYS'},
                        {'label': 'RESEARCH', 'value': 'RESEARCH'},
                        {'label': 'SHIPS', 'value': 'SHIPS'},
                        {'label': 'SHORE AND BOTTOM STATIONS', 'value': 'SHORE AND BOTTOM STATIONS'},
                        {'label': 'TIDE GAUGE STATIONS', 'value': 'TIDE GAUGE STATIONS'},
                        {'label': 'TROPICAL MOORED BUOYS', 'value': 'TROPICAL MOORED BUOYS'},
                        {'label': 'TSUNAMI WARNING STATIONS', 'value': 'TSUNAMI WARNING STATIONS'},
                        {'label': 'UNKNOWN', 'value': 'UNKNOWN'},
                        {'label': 'UNCREWED SURFACE VEHICLE', 'value': 'UNCREWED SURFACE VEHICLE'},
                        {'label': 'VOLUNTEER OBSERVING SHIPS', 'value': 'VOLUNTEER OBSERVING SHIPS'},
                        {'label': 'VOSCLIM', 'value': 'VOSCLIM'},
                        {'label': 'WEATHER AND OCEAN OBS', 'value': 'WEATHER AND OCEAN OBS'},
                        {'label': 'WEATHER BUOYS', 'value': 'WEATHER BUOYS'},
                        {'label': 'WEATHER OBS', 'value': 'WEATHER OBS'}
                    ]
                ),
                ddk.Row(ddk.Title('Color Markers by:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.RadioItems(
                    id='color-by',
                    options=[
                        {'label': 'Platform Type', 'value': 'platform_type'},
                        {'label': 'Country', 'value': 'country'},
                    ],
                    value=out_color_by
                ),
                ddk.Row(ddk.Title('Find Platforms:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.Dropdown(
                    id='platform-code',
                    clearable=True,
                    multi=False,
                    style={'padding-left': '10px'},
                    options=platform_code_options,
                    value = out_platform_code
                ),
                html.Hr(style={'border': '1px solid black'}),
                ddk.Row(ddk.Title('Plot Options:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.Dropdown(
                    id='markers',
                    options=[
                        {'label': 'Both lines and markers', 'value': 'both'},
                        {'label': 'Markers only', 'value': 'markers'},
                        {'label': 'Lines only', 'value': 'lines'}
                    ],
                    value='both',   
                ),
                html.Hr(style={'border': '1px solid black'}),
                ddk.Row(dcc.Loading(html.A(html.Button(id='download-button', children=['Download'], style={'font-size':'.8em', 'padding-left': '5px'},), target='_blank', id='download-link'))),
                dcc.Dropdown(
                    style={'margin-right': '5px'},
                    id='download-format',
                    options=[
                        {'label': 'CSV', 'value': '.csv'},
                        {'label': 'netCDF', 'value': '.ncCF'},
                        {'label': 'HTML', 'value': '.htmlTable'}
                    ],
                    placeholder='Select Download Format',   
                )
            ]
        )]

    return [control_block, out_line_marker_setting]


@app.callback([
    Output('platform-code', 'options'),
],[
    Input('variable', 'value'), 
    Input('platform-type', 'value'),
    Input('country', 'value'),
], prevent_initial_call=True)
def set_platform_list(list_variable_in, list_platform_type_in, list_country_in):
    map_df = db.get_locations()
    counts_df = db.get_counts()
    if list_variable_in is not None:
        query = ""
        if isinstance(list_variable_in, list):
            if len(list_variable_in) > 0:
                for qidx, qvar in enumerate(list_variable_in):
                    if qidx == 0:
                        query = query + qvar + '> 0'
                    else:
                        query = query + ' or ' + qvar + '> 0'
        elif isinstance(list_variable_in, str):
            query = query + list_variable_in + '> 0'
        if len(query) > 1:
            has_data = counts_df.query(query)
            map_df = map_df[map_df['platform_code'].isin(has_data['platform_code'])]

    if list_platform_type_in is not None:
        if isinstance(list_platform_type_in, str):
            map_df = map_df.loc[map_df['platform_type'] == list_platform_type_in]
        elif isinstance(list_platform_type_in, list):
            query = ''
            for pi, plat in enumerate(list_platform_type_in):
                if pi == 0:
                    query = query  + 'platform_type==\''+plat+'\''
                else:
                    query = query  + 'or platform_type==\''+plat+'\''
            if len(query) > 1:
                map_df = map_df.query(query)
    
    if list_country_in is not None:
        if isinstance(list_country_in, str):
            map_df = map_df.loc[map_df['country'] == list_country_in]
        elif isinstance(list_country_in, list):
            query = ''
            for ci, cntry in enumerate(list_country_in):
                if ci == 0:
                    query = query  + 'country==\''+cntry+'\''
                else:
                    query = query  + 'or country==\''+cntry+'\''
            if len(query) > 1:
                map_df = map_df.query(query)
    
    codes_to_show = pd.unique(map_df['platform_code'])
    platform_code_options = []
    codes_to_show.sort()
    for codey in codes_to_show:
       platform_code_options.append({'label': codey, 'value': codey})
    return [platform_code_options]



@app.callback([
    Output('map-info', 'data')
],[
    Input('location-map', 'relayoutData')
])
def record_map_change(relay_data):
    center = {'lon': 0.0, 'lat': 0.0}
    zoom = 1.4
    if relay_data is not None:
        if 'mapbox.center' in relay_data:
            center = relay_data['mapbox.center']
        if 'mapbox.zoom' in relay_data:
            zoom = relay_data['mapbox.zoom']
    map_info = {'center': center, 'zoom': zoom}
    return [json.dumps(map_info)]


@app.callback(
    [
        Output('platform-code', 'value')
    ],
    [
        Input('location-map', 'clickData')
    ], prevent_initial_call=True
)
def set_platform_code_from_map(state_in_click):
    out_platform_code = None
    if state_in_click is not None:
        fst_point = state_in_click['points'][0]
        out_platform_code = fst_point['customdata']
    return [out_platform_code]


@app.callback(
    [
        Output('ui-state', 'data'),
        Output('url', 'search')
    ],
    [
        Input('variable', 'value'), 
        Input('platform-type', 'value'),
        Input('country', 'value'),
        Input('color-by', 'value'),
        Input('platform-code', 'value'),
        Input('markers', 'value'),
    ],
    [
        State('map-info', 'data')
    ], prevent_initial_call=True
)
def set_ui_state(state_in_variable, state_in_platform_type, state_in_country, state_in_color_by, state_in_pcode, state_in_markers, state_in_map_info):
    trigger_id = ctx.triggered_id
    ui_state_out = {}
    query = '?'
    out_variable = None
    if state_in_variable is not None:
        if isinstance(state_in_variable, list):
            for vidx, v in enumerate(state_in_variable):
                if vidx == 0:
                    query = query + 'variable='+v
                else:
                   query = query + '&variable='+v
        else:
            query = query + 'variable='+out_variable
        out_variable = state_in_variable
        
    ui_state_out['variable'] = out_variable

    out_platform_type = None
    if state_in_platform_type is not None:
        out_platform_type = state_in_platform_type
        if isinstance(state_in_platform_type, list):
            for pt in state_in_platform_type:
                if len(query) > 1:
                    query = query + '&'
                query = query + 'platform_type=' + pt
        else:
            if len(query) > 1:
                query = query + '&'
            query = query + 'platform_type=' + out_platform_type
    ui_state_out['platform_type'] = out_platform_type

    out_country = None
    if state_in_country is not None:
        out_country = state_in_country
        if isinstance(state_in_country, list):
            for c in state_in_country:
                if len(query) > 1:
                    query = query + '&'
                query = query + 'country=' + c
        else:
            query = query + 'country=' + out_country
    ui_state_out['country'] = out_country

    out_color_by = 'platform_type'
    if state_in_color_by is not None:
        out_color_by = state_in_color_by
    if len(query) > 1:
        query = query + '&'
    query = query + 'color_by=' + out_color_by
    ui_state_out['color_by'] = out_color_by

    out_platform_code = state_in_pcode
    if out_platform_code is not None:
        if len(query) > 1:
            query = query + '&'
        query = query + 'platform_code=' + out_platform_code
    ui_state_out['platform_code'] = out_platform_code

    out_markers = 'both'
    if state_in_markers is not None:
        out_markers = state_in_markers
    ui_state_out['markers'] = out_markers

    if state_in_map_info is not None:
        query_map_info = json.loads(state_in_map_info)
        location_center = query_map_info['center']
        location_zoom = query_map_info['zoom']
        # query = query + '&lat=' + str(location_center['lat']) + '&lon=' + str(location_center['lon']) + '&zoom='+str(location_zoom)

    return [json.dumps(ui_state_out), query]

@app.callback(
    [
        Output('location-map', 'figure'),
        Output('map-card-header', 'children'),
        Output('map-loader', 'children'),
    ],
    [
        Input('ui-state', 'data'),
    ],
    [
        State('map-info', 'data')
    ], prevent_initial_call=True
)
def show_platforms(in_ui_state, map_in_map_info):
    
    cones_df = None
    try:
        cones_df = pd.read_csv(cones_url, skiprows=[1])
    except:
        print('load_platforms: No cones found.')

    if in_ui_state is not None and len(in_ui_state) > 0:
        map_ui_state = json.loads(in_ui_state)
    else:
        raise exceptions.PreventUpdate

    location_center = center
    location_zoom = zoom
    if map_in_map_info is not None:
        map_map_info = json.loads(map_in_map_info)
        location_center = map_map_info['center']
        location_zoom = map_map_info['zoom']

    map_df = db.get_locations()
    counts_df = db.get_counts()

    color_by = 'platform_type'
    if 'color_by' in map_ui_state:
        color_by = map_ui_state['color_by']

    if color_by == 'platform_type':
        color_map = platform_color
    if color_by == 'country':
        color_map = country_color

    platform_trace = None
    selection_code = None

    selection_code = map_ui_state['platform_code']
    if selection_code is not None:
        data_df = db.get_data(selection_code)
        trace_df = data_df.loc[data_df['platform_code']==selection_code]
        platform_trace = go.Scattermapbox(lat=trace_df["latitude"], lon=trace_df["longitude"], text=trace_df['trace_text'], mode='markers',
                                          marker=dict(color=trace_df["millis"], colorscale='Greys', size=13), name=str(selection_code),
                                          uid=9000)       
                                          

    map_in_variable = map_ui_state['variable']
    map_in_platform_type = map_ui_state['platform_type']
    map_in_country = map_ui_state['country']

    ui_revision = '*base*'

    if map_in_variable is not None:
        ui_revision = '*variable*'
        query = ""
        if isinstance(map_in_variable, list):
            if len(map_in_variable) > 0:
                for qidx, qvar in enumerate(map_in_variable):
                    if qidx == 0:
                        query = query + qvar + ' > 0'
                    else:
                        query = query + ' or ' + qvar + ' > 0'
        elif isinstance(map_in_variable, str):
            query = query + map_in_variable + ' > 0'
        if len(query) > 1:
            has_data = counts_df.query(query)
            map_df = map_df[map_df['platform_code'].isin(has_data['platform_code'])]

    if map_in_platform_type is not None:
        ui_revision = '*platform_type*'
        if isinstance(map_in_platform_type, str):
            map_df = map_df.loc[map_df['platform_type'] == map_in_platform_type]
        elif isinstance(map_in_platform_type, list):
            query = ''
            for pi, plat in enumerate(map_in_platform_type):
                if pi == 0:
                    query = query  + 'platform_type==\''+plat+'\''
                else:
                    query = query  + 'or platform_type==\''+plat+'\''
            if len(query) > 1:
                map_df = map_df.query(query)
    
    if map_in_country is not None:
        ui_revision = '*country*'
        if isinstance(map_in_country, str):
            map_df = map_df.loc[map_df['country'] == map_in_country]
        elif isinstance(map_in_country, list):
            query = ''
            for ci, cntry in enumerate(map_in_country):
                if ci == 0:
                    query = query  + 'country==\''+cntry+'\''
                else:
                    query = query  + 'or country==\''+cntry+'\''
            if len(query) > 1:
                map_df = map_df.query(query)

    platform_count = map_df.shape[0]
    title = 'Platform Locations - ' + str(platform_count) + ' platforms reported.'
    # In order to keep track of the traces that are selected and unselected, each trace has to have a unique ID.
    # The only way I've figured out how to do that is to make each trace for each category individually.  
    # The loop below replaces the px.scatter_mapbox call
    # location_map = px.scatter_mapbox(map_df, lat='latitude', lon='longitude',  
    #                                  color=color_by,
    #                                  color_discrete_map=color_map,
    #                                  hover_data=['platform_type', 'text_time', 'latitude', 'longitude', 'platform_code', 'country'],
    #                                  custom_data=['platform_code','platform_type'], 
    #                                  labels={"platform_type": "Platform Type"})
    location_map = go.Figure()
    categories = map_df[color_by].unique().tolist()
    categories.sort()
    for icat, category in enumerate(categories):
        map_trace_df = map_df.loc[map_df[color_by] == category]
        marker_color = color_map[category]
        platform_dots = go.Scattermapbox(lat=map_trace_df["latitude"], lon=map_trace_df["longitude"], mode='markers',
                                          marker=dict(color=marker_color, size=10), name=str(category),
                                          hovertext=map_trace_df['trace_text'],
                                          customdata=map_trace_df['platform_code'], 
                                          uid=icat)
        location_map.add_trace(platform_dots)
    location_map.update_layout(uirevision=ui_revision)
    if platform_trace is not None:
        location_map.add_trace(platform_trace)
    location_map.update_layout(
        height=map_height,
        mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "Powered by Esri",
                "source": [
                    "https://ibasemaps-api.arcgis.com/arcgis/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}?token=" + ESRI_API_KEY
                ]
            }
        ],
        mapbox_zoom=location_zoom,
        mapbox_center=location_center,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend=dict(
            orientation="v",
            x=-.01,
        ),
        modebar_orientation='v',
    )

    cone_colors = px.colors.qualitative.Light24

    if cones_df is not None and cones_df.shape[0] > 1:
        cones = cones_df['name'].unique()
        for inx, cone in enumerate(cones):                        
            fill_color = cc_color_set_transparent(inx, px.colors.qualitative.Light24, 0.5)
            line_color = cone_colors[inx]
            x = cones_df.loc[cones_df['name'] == cone, 'longitude']
            y = cones_df.loc[cones_df['name'] == cone, 'latitude']
            cone_map = go.Scattermapbox(lon=x,
                        lat=y,
                        mode='lines',
                        name=cone,
                        fill='toself',
                        hoverinfo='name',
                        hoverlabel={'namelength': -1},
                        fillcolor=fill_color,
                        line=dict(color=line_color))
            location_map.add_trace(cone_map)
    return [location_map, title, 'done']


@app.callback([
    Output('plots', 'figure'),
    Output('plots-header', 'title'),
    Output('download-url', 'data'),
    Output('download-format', 'value')
],[
    Input('ui-state', 'data')
], prevent_initial_call=True)
def make_plots(plot_in_ui_state):
    if plot_in_ui_state is not None:
        ui_state = json.loads(plot_in_ui_state)
    else:
        raise exceptions.PreventUpdate
    
    marker_menu = ui_state['markers']
    if marker_menu is None:
        marker_menu = 'lines+markers'
    elif marker_menu == 'both':
        marker_menu = 'lines+markers'

    selection_code = ui_state['platform_code']

    if selection_code is None:
         return [select_graph, 'Select a platform from the map or menu...', None, None]

    plot_df = db.get_data(selection_code)
    subplots = {}
    titles = []
    process_surf = 0
    plot_surf = 0
    plot_df = plot_df.loc[plot_df['platform_code']==selection_code]
    download_variables = []
    title_platform_type = plot_df['platform_type'].iloc[0]
    for var in constants.surface_variables:
        dfvar = plot_df[['time',var]].copy()
        dfvar.dropna(subset=[var], how='all', inplace=True) # do we want to drop nan or not, may have rows from other parameters that are "false" nan!!!
        if dfvar.shape[0] > 2:
            download_variables.append(var)
            varplot = go.Scatter(x=dfvar['time'], y=dfvar[var], name=var, mode=marker_menu)
            subplots[var] = varplot
            titles.append(var)
    for var in constants.depth_variables:
        dfvar = plot_df[['time', 'observation_depth', var]].copy()  
        dfvar = dfvar.sort_values(["time", "observation_depth"], ascending = (True, True))
        dfvar.dropna(subset=[var], how='all', inplace=True)
        colorscale='Inferno'
        if var == 'zsal':
            colorscale='Viridis'
        if dfvar.shape[0] > 2:
            download_variables.append(var)
            depths = pd.unique(dfvar['observation_depth'])
            if var == 'ztmp':
                xp = .45
            else:
                xp = 1.0
            if len(depths) > 1:
                varplot = go.Scattergl(x=dfvar['time'], y=dfvar['observation_depth'], 
                                     marker=dict(symbol='square', showscale=True, color=dfvar[var], colorscale=colorscale,),
                                     mode='markers', name=var, text=dfvar[var])
                titles.append(var)
            else:
                varplot = go.Scattergl(x=dfvar['time'], y=dfvar[var], name=var, mode=marker_menu, marker=dict(showscale=False))
                titles.append(var + ' at depth ' + str(depths[0]))
            subplots[var] = varplot

    num_plots = len(subplots)
    if num_plots == 0:
        return [no_data_graph, 'No data found for platform ' + str(selection_code), None, None]
    num_rows = int(num_plots/3)
    if num_rows == 0:
        num_rows = num_rows + 1
    if num_plots > 3 and num_plots%3 > 0:
        num_rows = num_rows + 1
    row_h = []
    for i in range(0, num_rows):
        row_h.append(1/num_rows)
    graph_height = height_of_row*num_rows
    num_cols = min(num_plots, 3)
    plots = make_subplots(rows=num_rows, cols=num_cols, shared_xaxes='all', subplot_titles=titles, shared_yaxes=False, row_heights=row_h)
    plot_index=1
    col=1
    row=1
    for plot in subplots:
        current_plot = subplots[plot]
        
        if plot == 'ztmp' or plot == 'zsal':
            if plot_index == 1: 
                yax = 'yaxis'
                xax = 'xaxis'
            else:
                yax = 'yaxis'+str(plot_index)
                xax = 'xaxis'+str(plot_index) 
            current_plot['marker']['colorbar']['len'] = plots['layout'][yax]['domain'][1]-plots['layout'][yax]['domain'][0]
            current_plot['marker']['colorbar']['y'] = (plots['layout'][yax]['domain'][1] + plots['layout'][yax]['domain'][0])/2
            current_plot['marker']['colorbar']['x'] = plots['layout'][xax]['domain'][1]
            current_plot['marker']['colorbar']['yanchor'] = 'middle'
            plots['layout'][yax]['autorange'] = "reversed"
        plots.add_trace(current_plot, row=row, col=col)
        plots.update_xaxes(title_text='Time', showticklabels=True, row=row, col=col)
        plots.update_yaxes(title_text=plot, showticklabels=True, row=row, col=col)
        plot_index = plot_index + 1
        if plot_index > 1:
            if col == 3:
                row = row + 1
        col = plot_index%3
        if col==0:
            col = 3

    plots.update_layout(height=graph_height, margin=dict( l=80, r=80, b=80, t=80, ))
    plots.update_traces(showlegend=False)
    plots_title = 'Plots for '+ str(title_platform_type) + ': ' + str(selection_code)
    download_url = data_url + '.csv?' + 'platform_code,platform_type,latitude,longitude,time,observation_depth,' + ','.join(download_variables) + '&orderBy("time,observation_depth")' + '&platform_code="' + selection_code + '"'
    return [plots, plots_title, download_url, None]

@app.callback(
    [
        Output('download-link', 'href'),
    ],
    [
        Input('download-format', 'value'),
    ],
    [     
        State('download-url', 'data')
    ], prevent_initial_call=True
)
def dowload_data(format_in, url_in):
    if url_in is None or format_in is None:
        url_out = None
    elif url_in is not None and format_in is not None:
        url_out = url_in.replace('.csv', format_in)
    return [url_out]


if __name__ == '__main__':
    app.run_server(debug=True)