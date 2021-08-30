import os

from sqlalchemy import create_engine
import pandas as pd
import geopandas as gpd


user = os.environ.get('DB_USERNAME')
pwd = os.environ.get('DB_PASSWORD')
host = os.environ.get('DB_HOSTNAME')
port = os.environ.get('DB_PORT')


class Base():
    'Hide the database code.'
    
    __url = f"postgres+psycopg2://{user}:{pwd}@{host}:{port}/geodemo"
    engine = create_engine(__url)

    def ls(self):
        'List database tables'
        
        sql = '''SELECT table_name
          FROM information_schema.tables
         WHERE table_schema='public'
           AND table_type='BASE TABLE';'''

        return list(pd.read_sql(sql, self.engine).table_name)
    
    def query(self, sql, spatial=False):
        'Query database.'
        
        if not spatial:
            return pd.read_sql(sql, self.engine)
        else:
            return gpd.read_postgis(sql, self.engine)
        
        
   