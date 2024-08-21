import constants
import pandas as pd
import datetime
from sqlalchemy import MetaData, Table


def trim(days_ago):
    n = datetime.datetime.now()
    r = n - datetime.timedelta(days=days_ago)
    delete = 'DELETE FROM {} WHERE TIME < \'' + r.isoformat() + '\';'
    print(delete)
    constants.postgres_engine.execute(delete.format(constants.data_table))

def delete_all():
    n = datetime.datetime.now()
    delete = 'DELETE FROM {};'
    print(delete.format(constants.data_table))
    constants.postgres_engine.execute(delete.format(constants.data_table))
    constants.postgres_engine.execute(delete.format(constants.counts_table))
    constants.postgres_engine.execute(delete.format(constants.locations_table))


def drop_all():
    metadata = MetaData()
    d_table = Table(constants.data_table, metadata)
    d_table.drop(constants.postgres_engine, checkfirst=True)
    c_table = Table(constants.counts_table, metadata)
    c_table.drop(constants.postgres_engine, checkfirst=True)
    l_table = Table(constants.locations_table, metadata)
    l_table.drop(constants.postgres_engine, checkfirst=True)


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
    selection = selection + ' ORDER BY TIME LIMIT 10000;'
    updated_df = pd.read_sql(
        selection.format(constants.data_table), constants.postgres_engine
    )
    return updated_df

def test_selection():
    selection = 'SELECT * from {}'
    selection = selection + ' WHERE PLATFORM_TYPE=\'ARGO\''
    selection = selection + ' ORDER BY TIME LIMIT 10;'
    updated_df = pd.read_sql(
        selection.format(constants.data_table), constants.postgres_engine
    )
    return updated_df

def exists():
    try:
        df = test_selection()
    except Exception as e:
        print(e)
        return False

    if df is not None:
        return True
    else:
        return False


def get_nobs(grouping):
    q = ''
    for var in constants.surface_variables:
        q = q + "COUNT({}) as {}, ".format(var, var)
    for var in constants.depth_variables:
        q = q + "COUNT({}) as {}, ".format(var, var)
    nobs_df = pd.read_sql(
        "SELECT {}, {} FROM {} GROUP BY {};".format(grouping, q[:-2], constants.data_table, grouping), constants.postgres_engine
    )
    nobs_df['total'] = nobs_df.sum(numeric_only=True, axis=1)
    return nobs_df


# https://stackoverflow.com/questions/121387/fetch-the-rows-which-have-the-max-value-for-a-column-for-each-distinct-value-of
def find_locations():
    query = f'''
        SELECT *, r.maxtime
        FROM (
            SELECT platform_code, MAX(time) as maxtime
            FROM osmc
            GROUP BY platform_code
        ) r
        INNER JOIN osmc t
        ON t.platform_code = r.platform_code AND t.time = r.maxtime
    '''
    locations = pd.read_sql(query, constants.postgres_engine)
    locations = locations.T.groupby(level=0).first().T
    # Get the last entry for variables with multiple depths (couldn't quite figure it out with sql)
    locations = locations.groupby('platform_code', as_index=False).last()
    return locations 


def get_platform_counts(grouping):
    platform_count = pd.read_sql(
        "SELECT {}, count(*) FROM {} GROUP BY {} ORDER BY {}".format(grouping, constants.locations_table, grouping, grouping), constants.postgres_engine
    )
    platform_dict = dict(zip(platform_count[grouping], platform_count['count']))
    return platform_count


def get_range(column):
    column_range = pd.read_sql(
        "SELECT min({}) AS min_{}, MAX({}) as max_{} FROM {}".format(column, column, column, column, constants.data_table), constants.postgres_engine
    )
    return column_range;

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
