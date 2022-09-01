from dash import Dash, dcc, html, Input, Output, State, exceptions, ctx
import dash_design_kit as ddk
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import zc
import constants
import db

import json
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

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

platform_color = {
    'ARGO' : '#0040FF',
    'AUTONOMOUS PINNIPEDS': '#FF0000',
    'C-MAN WEATHER STATIONS': '#FF7F00', 
    'CLIMATE REFERENCE MOORED BUOYS': '#FFD400', 
    'DRIFTING BUOYS': '#FFFF00', 
    'GLIDERS': '#BFFF00',
    'ICE BUOYS': '#6AFF00',
    'MOORED BUOYS': '#00EAFF',
    'RESEARCH': '#AA00FF',
    'SHIPS': '#FF00AA',
    'SHORE AND BOTTOM STATIONS': '#EDB9B9',
    'TIDE GAUGE STATIONS': '#E7E9B9',
    'TROPICAL MOORED BUOYS': '#B9EDE0',
    'TSUNAMI WARNING STATIONS': '#B9D7ED',
    'UNKNOWN': '#DCB9ED',
    'UNMANNED SURFACE VEHICLE': '#8F2323',
    'VOLUNTEER OBSERVING SHIPS': '#8F6A23',
    'VOSCLIM': '#23628F',
    'WEATHER AND OCEAN OBS': '#6B238F',
    'WEATHER BUOYS': '#000000',
    'WEATHER OBS': '#737373',
}

country_color = {
    'AUSTRALIA': px.colors.qualitative.Dark24[0],
    'BAHAMAS': px.colors.qualitative.Dark24[1],
    'BENIN': px.colors.qualitative.Dark24[2],
    'BERMUDA': px.colors.qualitative.Dark24[3],
    'BRAZIL': px.colors.qualitative.Dark24[4],
    'BULGARIA': px.colors.qualitative.Dark24[5],
    'CANADA': px.colors.qualitative.Dark24[6],
    'CHINA': px.colors.qualitative.Dark24[7],
    'CROATIA': px.colors.qualitative.Dark24[8],
    'EL SALVADOR': px.colors.qualitative.Dark24[9],
    'EUROPEAN UNION': px.colors.qualitative.Dark24[10],
    'FRANCE': px.colors.qualitative.Dark24[11],
    'GERMANY': px.colors.qualitative.Dark24[12],
    'GREECE': px.colors.qualitative.Dark24[13],
    'HONG KONG': px.colors.qualitative.Dark24[14],
    'INDIA': px.colors.qualitative.Dark24[15],
    'IRAN, ISLAMIC REPUBLIC OF': px.colors.qualitative.Dark24[16],
    'IRELAND': px.colors.qualitative.Dark24[17],
    'ISRAEL': px.colors.qualitative.Dark24[18],
    'ITALY': px.colors.qualitative.Dark24[19],
    'JAPAN': px.colors.qualitative.Dark24[20],
    'KOREA, REPUBLIC OF': px.colors.qualitative.Dark24[21],
    'MARSHALL ISLANDS': px.colors.qualitative.Dark24[22],
    'NETHERLANDS': px.colors.qualitative.Dark24[23],
    'NEW ZEALAND': px.colors.qualitative.Light24[0],
    'NORWAY': px.colors.qualitative.Light24[1],
    'PHILIPPINES': px.colors.qualitative.Light24[2],
    'POLAND': px.colors.qualitative.Light24[3],
    'PORTUGAL': px.colors.qualitative.Light24[4],
    'ROMANIA': px.colors.qualitative.Light24[5],
    'RUSSIAN FEDERATION': px.colors.qualitative.Light24[6],
    'SOUTH AFRICA': px.colors.qualitative.Light24[7],
    'SPAIN': px.colors.qualitative.Light24[8],
    'SYRIAN ARAB REPUBLIC': px.colors.qualitative.Light24[9],
    'UNITED KINGDOM': px.colors.qualitative.Light24[10],
    'UNITED STATES': px.colors.qualitative.Light24[11],
    'UNKNOWN': px.colors.qualitative.Light24[12],
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
    dcc.Location(id='url'),
    html.Div(id='window-info', style={'display': 'none'}),
    dcc.Store(id='map-info'),
    ddk.Header([
        ddk.Logo(src=app.get_asset_url('pmel-emblem-rgb-2022.png'), style={'height':'90px'}),
        ddk.Title('Observing System Monitoring Center'),
        dcc.Loading(html.Div(id='map-loader', style={'float': 'right', 'display': 'none'}))
    ]),
    ddk.Block (width=20, children=[
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
                        {'value': "BRAZIL", 'label': 'Brazil'},
                        {'value': "CANADA", 'label': 'Canada'},
                        {'value': "CHINA", 'label': 'China'},
                        {'value': "EUROPEAN UNION", 'label': 'European Union'},
                        {'value': "FRANCE", 'label': 'France'},
                        {'value': "GERMANY", 'label': 'Germany'},
                        {'value': "INDIA", 'label': 'India'},
                        {'value': "IRELAND", 'label': 'Ireland'},
                        {'value': "JAPAN", 'label': 'Japan'},
                        {'value': "KOREA, REPUBLIC OF", 'label': 'South Korea'},
                        {'value': "SPAIN", 'label': 'Spain'},
                        {'value': "NETHERLANDS", 'label': 'Netherlands'},
                        {'value': "NEW ZEALAND", 'label': 'New Zealand'},
                        {'value': "NORWAY", 'label': 'Norway'},
                        {'value': "SOUTH AFRICA", 'label': 'South Africa'},
                        {'value': "UKRAINE", 'label': 'Ukraine'},
                        {'value': "UNITED KINGDOM", 'label': 'United Kingdom'},
                        {'value': "UNITED STATES", 'label': 'United States'},
                    ]
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
                    ]
                ),
                ddk.Row(ddk.Title('Platform Type:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.Dropdown(
                    id='platform-type',
                    clearable=True,
                    multi=True,
                    style={'padding-left': '10px'},
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
                    value='platform_type'
                ),
                ddk.Row(ddk.Title('Find Platforms:', style={'font-size':'.8em', 'padding-left': '5px'})),
                dcc.Dropdown(
                    id='platform-code',
                    clearable=True,
                    multi=False,
                    style={'padding-left': '10px'},
                    options=[
                        
                    ]
                )
            ]
        )
    ]),
    ddk.Block(width=80, children=[
        ddk.Card(children=[
            ddk.CardHeader(id='map-card-header', modal=True, modal_config={'height': 90, 'width': 95}, fullscreen=True),
            ddk.Graph(id='location-map', style={'padding-left': '20px'}),
        ]),
    ]),
    ddk.Block(width=100, children=[
        ddk.Card(children=[
            dcc.Loading(
                ddk.CardHeader(id='plots-header', modal=True, modal_config={'height': 90, 'width': 95}, fullscreen=True)
            ),
            ddk.Graph(id='plots', style={'padding-left': '20px'}),
        ]),
    ]),
])


@app.callback([
    Output('platform-code', 'options')
],[
    Input('variable', 'value'), 
    Input('platform-type', 'value'),
    Input('country', 'value'),
])
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


app.clientside_callback(
    """
    function(href) {
        var w = window.innerWidth;
        var h = window.innerHeight;
        return JSON.stringify({'height': h, 'width': w});
    }
    """,
    Output('window-info', 'children'),
    Input('url', 'href')
)


@app.callback(
    [
        Output('platform-code', 'value'),
    ],
    [
        Input('location-map', 'clickData'),
    ]
)
def set_platform_from_map(in_map_clicky):
    selection_value = None
    if in_map_clicky is not None:
        fst_point = in_map_clicky['points'][0]
        selection_value = fst_point['customdata'][0]
    return [selection_value]


@app.callback(
    [
        Output('location-map', 'figure'),
        Output('map-card-header', 'children'),
        Output('map-loader', 'children')
    ],
    [
        Input('variable', 'value'), 
        Input('platform-type', 'value'),
        Input('country', 'value'),
        Input('color-by', 'value'),
        Input('location-map', 'clickData'),
        Input('platform-code', 'value'),
        Input('window-info', 'children')
    ],
    [
        State('map-info', 'data')
    ]
)
def show_platforms(map_in_variable, map_in_platform_type, map_in_country, map_in_color_by, map_in_click, map_in_pcode, map_in_window_info, map_in_map_info):

    map_h = 800/2

    location_center = center
    location_zoom = zoom
    if map_in_map_info is not None:
        map_map_info = json.loads(map_in_map_info)
        location_center = map_map_info['center']
        location_zoom = map_map_info['zoom']

    map_df = db.get_locations()
    counts_df = db.get_counts()

    color_by = 'platform_type'
    if map_in_color_by is not None:
        color_by = map_in_color_by

    if color_by == 'platform_type':
        color_map = platform_color
    if color_by == 'country':
        color_map = country_color

    platform_trace = None
    selection_code = None

    input_id = ctx.triggered_id if not None else 'No platform'
    if input_id == 'location-map' and map_in_click is not None:
        fst_point = map_in_click['points'][0]
        selection_code = fst_point['customdata'][0]
    if input_id == 'platform-code' and map_in_pcode is not None:
        selection_code = map_in_pcode
    if selection_code is not None:
        data_df = db.get_data(selection_code)
        trace_df = data_df.loc[data_df['platform_code']==selection_code]
        platform_trace = go.Scattermapbox(lat=trace_df["latitude"], lon=trace_df["longitude"], text=trace_df['trace_text'], mode='markers',
                                          marker=dict(color=trace_df["millis"], colorscale='cividis_r', size=13), name=str(selection_code))
                        
                                          
    if map_in_window_info is not None:
        w_size = json.loads(map_in_window_info)
        map_h = (w_size['height'] - header_footer_fudge)/2

    if map_in_variable is not None:
        query = ""
        if isinstance(map_in_variable, list):
            if len(map_in_variable) > 0:
                for qidx, qvar in enumerate(map_in_variable):
                    if qidx == 0:
                        query = query + qvar + '> 0'
                    else:
                        query = query + ' or ' + qvar + '> 0'
        elif isinstance(map_in_variable, str):
            query = query + map_in_variable + '> 0'
        if len(query) > 1:
            has_data = counts_df.query(query)
            map_df = map_df[map_df['platform_code'].isin(has_data['platform_code'])]

    if map_in_platform_type is not None:
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
    location_map = px.scatter_mapbox(map_df, lat='latitude', lon='longitude',  
                                     color=color_by,
                                     color_discrete_map=color_map,
                                     hover_data=['text_time', 'latitude', 'longitude', 'platform_code'],
                                     custom_data=['platform_code','platform_type'], 
                                     labels={"platform_type": "Platform Type"}
                                    )
    location_map.update_traces(marker_size=10, unselected=dict(marker=dict(opacity=.55)),)
    if platform_trace is not None:
        location_map.add_trace(platform_trace)
    location_map.update_layout(
        height=map_h,
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
    return [location_map, title, 'done']


@app.callback([
    Output('plots', 'figure'),
    Output('plots-header', 'children'),
],[
    Input('location-map', 'clickData'),
    Input('platform-code', 'value')
], prevent_initial_call=True)
def make_plots(selection_click, selection_menu):
    
    if selection_click is None and selection_menu is None:
        return [select_graph, 'Click on a platform on the map or select one from the menu...']

    selection_code = None
    input_id = ctx.triggered_id if not None else 'No platform'
    if input_id == 'location-map' and selection_click is not None:
        fst_point = selection_click['points'][0]
        selection_code = fst_point['customdata'][0]
    if input_id == 'platform-code' and selection_menu is not None:
        selection_code = selection_menu
    
    if selection_code is None:
        return [select_graph, 'Click on a platform on the map or select one from the menu...']

    plot_df = db.get_data(selection_code)
    subplots = {}
    titles = []
    process_surf = 0
    plot_surf = 0
    plot_df = plot_df.loc[plot_df['platform_code']==selection_code]
    title_platform_type = plot_df['platform_type'].iloc[0]
    for var in constants.surface_variables:
        dfvar = plot_df[['time',var]].copy()
        dfvar.dropna(subset=[var], how='all', inplace=True) # do we want to drop nan or not, may have rows from other parameters that are "false" nan!!!
        if dfvar.shape[0] > 2:
            varplot = go.Scatter(x=dfvar['time'], y=dfvar[var], name=var, mode='lines+markers')
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
                varplot = go.Scattergl(x=dfvar['time'], y=dfvar[var], name=var, mode='lines+markers', marker=dict(showscale=False))
                titles.append(var + ' at depth ' + str(depths[0]))
            subplots[var] = varplot

    num_plots = len(subplots)
    if num_plots == 0:
        return [no_data_graph, 'No data found for platform ' + str(selection_code)]
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
    return [plots, plots_title]

if __name__ == '__main__':
    app.run_server(debug=True)