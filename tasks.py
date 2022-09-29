import os
import redis
import pandas as pd
import numpy as np
import json
from celery import Celery
from celery.schedules import crontab

from celery.utils.log import get_task_logger

from random import randrange

import constants
import db

logger = get_task_logger(__name__)

celery_app = Celery('tasks', broker=os.environ.get("REDIS_URL", "redis://127.0.0.1:6379"))

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
         crontab(minute='45'),
         append_new_observations.s(),
         name='Append New Observations'
    )
    sender.add_periodic_task(
         crontab(hour='1'),
         trim_database.s(),
         name='Delete observations older than 45 days'
    )


@celery_app.task
def load_observations():
    #url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/osmc_rt_60.csv?' + constants.all_variables_comma_separated + '&time>=2022-08-01T00:00:00Z'
    #url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/osmc_rt_60.csv?' + constants.all_variables_comma_separated
    url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/osmc_rt_60.csv?' + constants.all_variables_comma_separated + '&time>=now-45days'

    logger.info('Reading data from ' + url)

    df = pd.read_csv(url, skiprows=[1], dtype=constants.dtypes, parse_dates=True)

    df = df.dropna(subset=['latitude','longitude'], how='any')
    df = df.query('-90.0 <= latitude <= 90')
    df = df.sort_values('time')
    df.reset_index(drop=True, inplace=True)
    df.loc[:,'millis'] = pd.to_datetime(df['time']).view(np.int64)
    df.loc[:,'text_time'] = df['time'].astype(str)
    # ['platform_type', 'text_time', 'latitude', 'longitude', 'platform_code', 'country'],
    df.loc[:,'trace_text'] = df['text_time'] + "<br>" + df['platform_type'] + "<br>" + df['country'] + "<br>" + df['platform_code']

    logger.info('Preparing sub-sets for locations and counts.')
    locations_df = df.groupby('platform_code', as_index=False).last()

    counts_df = df.groupby('platform_code').count()
    counts_df.reset_index(inplace=True)

    logger.info('Found ' + str(df.shape[0]) + ' observations to store.')

    # In the following command, we are saving the updated new data to the dataset_table using pandas
    # and the SQLAlchemy engine we created above. When if_exists='append' we add the rows to our table
    # and when if_exists='replace', a new table overwrites the old one.
    logger.info('Updating data...')
    df.to_sql(constants.data_table, constants.postgres_engine, if_exists='replace', index=False, chunksize=1500, method='multi')
    logger.info('Updating counts...')
    counts_df.to_sql(constants.counts_table, constants.postgres_engine, if_exists='replace', index=False)
    logger.info('Updating locations...')
    locations_df.to_sql(constants.locations_table, constants.postgres_engine, if_exists='replace', index=False)


@celery_app.task
def trim_database():
    db.trim(45)


@celery_app.task
def append_new_observations():
    #url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/osmc_rt_60.csv?' + constants.all_variables_comma_separated + '&time>=2022-08-01T00:00:00Z'
    #url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/osmc_rt_60.csv?' + constants.all_variables_comma_separated
    url = 'https://data.pmel.noaa.gov/pmel/erddap/tabledap/osmc_rt_60.csv?' + constants.all_variables_comma_separated + '&time>=now-14days'

    logger.info('Reading data from ' + url)

    df = pd.read_csv(url, skiprows=[1], dtype=constants.dtypes, parse_dates=True)
    
    df = df.dropna(subset=['latitude','longitude'], how='any')
    df = df.query('-90.0 <= latitude <= 90')
    df = df.sort_values('time')
    df.reset_index(drop=True, inplace=True)
    df.loc[:,'millis'] = pd.to_datetime(df['time']).view(np.int64)
    df.loc[:,'text_time'] = df['time'].astype(str)
    df.loc[:,'trace_text'] = df['text_time'] + "<br>" + df['platform_type'] + "<br>" + df['country'] + "<br>" + df['platform_code']
    columns = df.columns
    df = df.assign(source='erddap')
    logger.info('read ' + str(df.shape[0]) + ' potential new observations')
    
    for days in range(0,9):
        ago1 = 45-((days+1)*5)
        ago2 = 45-(days*5)
        logger.info('checking for duplicates in days: ' + str(ago1) + ' to ' + str(ago2) + ' ago.' )
        stored_df = db.get_between_days_ago(ago1, ago2)
        stored_df = stored_df.assign(source='db')
        logger.info(str(stored_df.shape[0]) + ' obervations found in database.')
        df = pd.concat([stored_df, df])
        df.reset_index(inplace=True, drop=True)
        PRECISION = 3
        df.drop(df[['latitude', 'longitude', 'observation_depth','millis']].round(PRECISION).duplicated().loc[lambda latitude: latitude].index, inplace=True)
        df = df[df['source']=='erddap']
        logger.info(str(df.shape[0]) + ' observations that are not stored remain after checking this day range.')

    df = df[columns]
    df = df.dropna(subset=['latitude','longitude'], how='any')
    df = df.query('-90.0 <= latitude <= 90')
    df = df.sort_values('time')
    df.reset_index(drop=True, inplace=True)
    logger.info('First row=')
    logger.info(df.iloc[0])
    logger.info('Last row=')
    logger.info(df.iloc[-1])
    logger.info('Found ' + str(df.shape[0]) + ' new observations to append.')


    # In the following command, we are saving the updated new data to the dataset_table using pandas
    # and the SQLAlchemy engine we created above. When if_exists='append' we add the rows to our table
    # and when if_exists='replace', a new table overwrites the old one.
    logger.info('Updating data...')
    if df.shape[0] > 0:
        df.to_sql(constants.data_table, constants.postgres_engine, if_exists='append', index=False, chunksize=1500, method='multi')

    # These are small and should be made to match the data in the database, so replace them
    df = db.get_data(None)
    logger.info('Preparing sub-sets for locations and counts.')
    locations_df = df.groupby('platform_code', as_index=False).last()

    counts_df = df.groupby('platform_code').count()
    counts_df.reset_index(inplace=True)

    logger.info('Updating counts...')
    counts_df.to_sql(constants.counts_table, constants.postgres_engine, if_exists='replace', index=False)
    logger.info('Updating locations...')
    locations_df.to_sql(constants.locations_table, constants.postgres_engine, if_exists='replace', index=False)

    
@celery_app.task
def counts_and_location():
    df = db.get_data(None)
    logger.info('Preparing sub-sets for locations and counts.')
    locations_df = df.groupby('platform_code', as_index=False).last()

    counts_df = df.groupby('platform_code').count()
    counts_df.reset_index(inplace=True)

    logger.info('Updating counts...')
    counts_df.to_sql(constants.counts_table, constants.postgres_engine, if_exists='replace', index=False)
    logger.info('Updating locations...')
    locations_df.to_sql(constants.locations_table, constants.postgres_engine, if_exists='replace', index=False)