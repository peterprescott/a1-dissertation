import os

from sqlalchemy import create_engine
import pandas as pd
import geopandas as gpd


user = os.environ.get('DB_USERNAME')
pwd = os.environ.get('DB_PASSWORD')
host = os.environ.get('DB_HOSTNAME')
port = os.environ.get('DB_PORT')

# note that 27700 is the British National Grid reference number.


class Base():
    'Hide the database code.'
    
    __url = f"postgres+psycopg2://{user}:{pwd}@{host}:{port}/geodemo"
    print('Initializing database connection...')
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
        
        if 'ST_' in sql:
            spatial = True
        
        if not spatial:
            return pd.read_sql(sql, self.engine)
        else:
            return gpd.read_postgis(sql, self.engine, geom_col='geometry')
    
    def within(self, table, buffer, x=338157, y=393037):
        sql = f'''
        SELECT * FROM {table} 
        WHERE ST_DWithin(
            geometry, 
            ST_SetSRID(ST_Point({x}, {y}), 27700), 
            {buffer})
        '''
#         return gpd.read_postgis(sql, self.engine, geom_col='geometry')
        return self.query(sql)
        
    def contains(self, table, polygon):
        sql = f'''
        SELECT
        * from {table}
        WHERE 
            ST_Contains(ST_GeomFromText('{polygon}', 27700), geometry); 
        '''
        return self.query(sql)
        
   