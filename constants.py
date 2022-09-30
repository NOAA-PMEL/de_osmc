import numpy as np
import redis
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import os

meta_variables = ['longitude', 'latitude', 'observation_depth', 'time', 'platform_type', 'platform_code', 'country']
surface_variables = ['sst','atmp','slp','windspd','winddir','clouds','dewpoint',]
unused_variables = ['uo','vo','wo','waterlevel','rainfall_rate','hur','sea_water_elec_conductivity','sea_water_pressure','rlds','rsds','waterlevel_met_res','waterlevel_wrt_lcd','water_col_ht','wind_to_direction']
depth_variables = ['ztmp','zsal']

units = {
    'sst':'Deg C',
    'atmp': 'Deg C',
    'slp': 'hPa',
    'windspd': 'm/s',
    'winddir': 'Deg true',
    'clouds': 'oktas',
    'dewpoint': 'Deg C',
    'ztmp': 'Deg C',
    'zsal': 'PSU'
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
    'platform_code':str
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
connection_string = "postgresql+pg8000" + os.environ.get(
    "DATABASE_URL", "postgresql://postgres:password@127.0.0.1:5432"
).lstrip("postgresql")

# Create a SQLAlchemy engine object. This object initiates a connection pool
# so we create it once here and import into app.py.
# `poolclass=NullPool` prevents the Engine from using any connection more than once. You'll find more info here:
# https://docs.sqlalchemy.org/en/14/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
postgres_engine = create_engine(connection_string, poolclass=NullPool)

