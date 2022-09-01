import constants
import pandas as pd
import datetime


def trim(days_ago):
    delete = 'DELETE from {} WHERE TIME < NOW() - \''+str(days_ago)+' days\'::interval;'
    print(delete)
    ## DEBUG constants.postgres_engine.execute(delete.format(constants.data_table))


def get_between_days_ago(ago1, ago2):
    if ago1 == ago2:
        return

    if ago1 > ago2:
        t = ago1
        ago1 = ago2
        ago2 = t

    since1 = datetime.datetime.now() - datetime.timedelta(days = ago1) 
    since2 = datetime.datetime.now() - datetime.timedelta(days = ago2) 
    selection = 'SELECT * from {} WHERE TIME BETWEEN \''+since2.isoformat()+'\' AND \''+since1.isoformat()+'\' ORDER BY TIME';
    stored_df = pd.read_sql(
        selection.format(constants.data_table), constants.postgres_engine
    )
    return stored_df


def get_data(platform):
    # In this function, we retrieve the data from postgres using pandas's read_sql method.

    # This data is periodically getting updated via a separate Celery Process in tasks.py.
    # "dataset_table" is the name of the table that we initialized in tasks.py.
    selection = 'SELECT * from {}'
    if platform is not None:
        selection = selection + ' WHERE PLATFORM_CODE=\'' + str(platform) +'\''
    selection = selection + ' ORDER BY TIME;'
    updated_df = pd.read_sql(
        selection.format(constants.data_table), constants.postgres_engine
    )
    return updated_df


def get_counts():
    # In this function, we retrieve the data from postgres using pandas's read_sql method.

    # This data is periodically getting updated via a separate Celery Process in tasks.py.
    # "dataset_table" is the name of the table that we initialized in tasks.py.
    updated_df = pd.read_sql(
        "SELECT * FROM {};".format(constants.counts_table), constants.postgres_engine
    )
    return updated_df


def get_locations():
    # In this function, we retrieve the data from postgres using pandas's read_sql method.

    # This data is periodically getting updated via a separate Celery Process in tasks.py.
    # "dataset_table" is the name of the table that we initialized in tasks.py.
    updated_df = pd.read_sql(
        "SELECT * FROM {};".format(constants.locations_table), constants.postgres_engine
    )
    return updated_df
