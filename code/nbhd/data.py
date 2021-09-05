import os

import pandas as pd
import geopandas as gpd
import networkx as nx

from sqlalchemy import create_engine


class Base():
    'Hide the database code.'
    
    def __init__(self, user=None, pwd=None, host=None, port=None, db=None):
        if not user:
            user = os.environ.get('DB_USERNAME')
        if not pwd:
            pwd = os.environ.get('DB_PASSWORD')
        if not host:
            host = os.environ.get('DB_HOSTNAME')
        if not port:
            port = os.environ.get('DB_PORT')
        if not db:
            db = os.environ.get('DB_DATABASE')


        __url = f"postgres+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
        print('Initializing database connection...')
        self.engine = create_engine(__url)
        count_tables = len(self.ls())
        print('Database connected!')

    
    def query(self, sql, spatial=False):
        'Query database.'

        if not spatial:
            return pd.read_sql(sql, self.engine)
        else:
            return gpd.read_postgis(sql, self.engine, geom_col='geometry')
    
    def ls(self):
        'List database tables'
        
        sql = '''SELECT table_name
          FROM information_schema.tables
         WHERE table_schema='public'
           AND table_type='BASE TABLE';'''

        return list(pd.read_sql(sql, self.engine).table_name)

    def info(self, table_name):
        sql = f'''
            SELECT
                a.attname as "Column",
                pg_catalog.format_type(a.atttypid, a.atttypmod) as "Datatype"
            FROM
                pg_catalog.pg_attribute a
            WHERE
                a.attnum > 0
                AND NOT a.attisdropped
                AND a.attrelid = (
                    SELECT c.oid
                    FROM pg_catalog.pg_class c
                        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relname = '{table_name}'
                        AND pg_catalog.pg_table_is_visible(c.oid)
                );
            '''
        return self.query(sql)
    
    
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
    
    def _spatial_query(self, table, st_query, polygon, crs=27700):
        sql = f'''
             SELECT * from {table}
                WHERE ST_{st_query.capitalize()}(
                    geometry,
                    ST_GeomFromText('{polygon}', {crs})
                    )
        '''
        return sql

    def contains(self, table, polygon):
        sql = self._spatial_query(table, 'contains', polygon)
        return self.query(sql, spatial=True)

    def crosses(self, table, polygon):
        sql = self._spatial_query(table, 'crosses', polygon)
        return self.query(sql, spatial=True)

    def disjoint(self, table, polygon):
        sql = self._spatial_query(table, 'disjoint', polygon)
        return self.query(sql, spatial=True)

    def equals(self, table, polygon):
        sql = self._spatial_query(table, 'equals', polygon)
        return self.query(sql, spatial=True)

    def intersects(self, table, polygon):
        sql = self._spatial_query(table, 'intersects', polygon)
        return self.query(sql, spatial=True)

    def overlaps(self, table, polygon):
        sql = self._spatial_query(table, 'overlaps', polygon)
        return self.query(sql, spatial=True)

    def touches(self, table, polygon):
        sql = self._spatial_query(table, 'touches', polygon)
        return self.query(sql, spatial=True)

    def within(self, table, polygon):
        sql = self._spatial_query(table, 'within', polygon)
        return self.query(sql, spatial=True)

    def covers(self, table, polygon):
        sql = self._spatial_query(table, 'covers', polygon)
        return self.query(sql, spatial=True)

    def coveredBy(self, table, polygon):
        sql = self._spatial_query(table, 'coveredBy', polygon)
        return self.query(sql, spatial=True)

    def containsProperly(self, table, polygon):
        sql = self._spatial_query(table, 'containsProperly', polygon)
        return self.query(sql, spatial=True)

    def knn(self, table1, table2, polygon, k=1, max_distance=None, spatial_query='intersects'):
        '''
        Find k nearest-neighbours for results from table1 and table2 
        as returned by given spatial_query for given polygon.
        '''
        difference_condition = ''
        maximum_condition = ''
        
        sql_table1 = self._spatial_query(table1, spatial_query, polygon)
        
        if table2 == table1:
            sql_table2 = sql_table1
            difference_condition = 'WHERE t1.id != t2.id'
        else:
            sql_table2 = self._spatial_query(table2, spatial_query, polygon)
        
        if max_distance:
            if difference_condition:
                start_word = 'AND'
            else:
                start_word = 'WHERE'
            maximum_condition = f'''{start_word} ST_Distance(
                        t1.geometry, t2.geometry
                        ) < {max_distance}'''
        
        sql = f'''
        SELECT t1.*,
               t2.*,
               ST_Distance(t1.geometry, t2.geometry) AS dist
        FROM ({sql_table1}) AS t1
        CROSS JOIN LATERAL (
          SELECT t2.* 
          FROM ({sql_table2}) AS t2
          {difference_condition}
          {maximum_condition}
          ORDER BY t1.geometry <-> t2.geometry
          LIMIT {k}
        ) AS t2 ;
        '''
        
        return self.query(sql)

    def nn_translator(self, table, polygon, max_distance):
        nearest_nodes = self.knn(table, table, 
                                 polygon, k=100, max_distance=max_distance)
        g = nx.from_pandas_edgelist(nearest_nodes, 'id_1', 'id_2', True)
        subgraphs = [g.subgraph(c) for c in nx.connected_components(g)]
        translator = {n: list(g.nodes)[0] for g in subgraphs for n in g.nodes}
        return translator