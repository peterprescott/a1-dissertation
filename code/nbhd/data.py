import os

import pandas as pd
import geopandas as gpd

from sqlalchemy import create_engine


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
    print('Database connected!')

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
            return gpd.read_postgis(sql, self.engine, geom_col='geometry')
    
    def select(self, table):
        if table in self.ls():
            sql = f'SELECT * FROM {table}'
            return gpd.read_postgis(sql, self.engine, geom_col='geometry')
        else:
            print(f'`{table}` is not a table in the database.')
            return None
    
    def within(self, table, buffer, x=338157, y=393037):
        sql = f'''
        SELECT * FROM {table} 
        WHERE ST_DWithin(
            geometry, 
            ST_SetSRID(ST_Point({x}, {y}), 27700), 
            {buffer})
        '''
        return self.query(sql, spatial=True)
        
    def contains(self, table, polygon):
        sql = self._contains_query(table, polygon)
        return self.query(sql, spatial=True)
        
    def _contains_query(self, table, polygon):
        return f'''
                SELECT * from {table}
                    WHERE ST_Contains(
                        ST_GeomFromText('{polygon}', 27700), 
                    geometry) 
        '''

    def nearest_neighbours(self, table, boundary_wkt):
        sql = f'''
        SELECT "UPRN",
               dbtable.id AS id,
               ST_Distance(dbtable.geometry, uprn.geometry) AS dist
        FROM ({self._contains_query('openuprn', boundary_wkt)}) AS uprn
        CROSS JOIN LATERAL (
          SELECT dbtable.geometry, dbtable.id
          FROM ({self._contains_query(table, boundary_wkt)}) AS dbtable 
          ORDER BY dbtable.geometry <-> uprn.geometry
          LIMIT 1
        ) dbtable;
        '''
        return self.query(sql, spatial=False)
