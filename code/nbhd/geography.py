'''Geographical analysis.'''

from time import time

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Voronoi

from shapely.geometry import (Point,
                              LineString,
                              Polygon, 
                              MultiPolygon)
from shapely.ops import polygonize
from mapclassify import greedy

from .data import Base
from .geometry import tessellate, cellularize


class Neighbourhood:
    '''
    Theoretically-informed and data-driven neighbourhood analysis.
    '''

    def __init__(self, easting=338172, northing=391744, db=Base(), load=True):
        '''Begin with a point on the British National Grid.'''
        
        self.db = db
        # find enclosure from database
        
        enclosures = db.within('bigtilesa', 0, easting, northing)
        if len(enclosures) == 1:
            self.geom = enclosures.geometry[0]
        else:
            print('boundary point!')
            self.geom = MultiPolygon(
                list(enclosures.geometry))
            
        self.boundary = gpd.GeoSeries(self.geom.boundary)
        
        if load:
            self.get_data()
    
    def get_communities(self, 
                    footprint_threshold=250, 
                    res_length_threshold=30, 
                    short_threshold=50, 
                    min_community_size=0, 
                    node_distance=30):

        # nearest roads ~ 'slimroads' is without motorways and secondary roads
        nr_roads = n.db.nearest_neighbours('openroads', n.geom.buffer(10))
        # nearest buildings
        nr_buildings = n.db.nearest_neighbours('openmaplocal', n.geom.buffer(1))
        # merge on UPRN
        df = nr_buildings.merge(nr_roads, on=['UPRN', 'uprn_geometry'], 
                                how='inner', suffixes=('_building', '_street'))

        # 1 eliminate non-building properties : distance to building must == 0
        df1 = df.loc[df.dist_building==0]

        # 2 eliminate non-residential buildings : area / uprn count must < 250
        building_counts = dict(df1.id_building.value_counts())
        df1['building_counts'] = df1.id_building.apply(lambda x: building_counts.get(x, 0))
        df1['footprint_area'] = gpd.GeoSeries(df1.geometry_building).area
        df1['footprint_area_per_uprn'] = df1.footprint_area / df1.building_counts
        df1['residential_building'] = df1['footprint_area_per_uprn'] < footprint_threshold
        df2 = df1.loc[df1.residential_building]

        # 3 establish whether roads are residential : length / uprn count must < 5??
        street_counts = dict(df2.id_street.value_counts())
        df2['street_counts'] = df2.id_street.apply(lambda x: street_counts.get(x, 0))
        df2['street_length_per_uprn'] = df2.length / df2.street_counts
        df2['residential_street'] = df2.street_length_per_uprn < res_length_threshold
        residential = dict(zip(df2.id_street, df2.residential_street))
        df['residential'] = df.id_street.apply(lambda x: residential.get(x, False))
        df['short_street'] = df.length < short_threshold
        df['res_or_short'] = df.residential | df.short_street
        df3 = df.loc[df.res_or_short]

        # 4 treat nearby nodes as equivalent
        translator = db.get_nearest_nodes_translator(self, node_distance)
        edges = df3.loc[~df3.duplicated()]
        edges['translated_start'] = edges.startNode.apply(lambda x: translator.get(x, x))
        edges['translated_end'] = edges.endNode.apply(lambda x: translator.get(x, x))

        # 5 find connected networks of residential streets
        g = nx.from_pandas_edgelist(edges, 'translated_start', 'translated_end', True)
        subgraphs =[g.subgraph(c) for c in nx.connected_components(g)]
        sgs = [sg for sg in subgraphs if len(sg) > 1]

        # 6 add community labels
        communities = dict()
        for i in range(len(sgs)):
            communities[str(i).zfill(2)] = list(nx.get_edge_attributes(sgs[i], 'id_street').values())
        communities_key = {value:key for key, value_list 
                           in communities.items() for value in value_list}

        df['community'] = df.id_street.apply(lambda x: communities_key.get(x, None))
        self.df = df
        return
        
    def get_data(self, wanted=('roads', 'uprn', 'buildings'), 
                 plus=None, silent=True):
        
        t0 = time()
        
        wanted_list = list(wanted)
        if plus:
            wanted_list.extend(plus)
        
        table = {'roads': 'openroads',
                  'uprn': 'openuprn',
                  'buildings': 'openmaplocal',
                  'rail': 'railways',
                  'rivers': 'rivers'}
        
        for w in wanted_list:
            # need to buffer this slightly
            setattr(self, w, self.db.contains(table[w], self.geom.buffer(1).wkt))
        
        t1 = time()
        t = t1 - t0
        print(('Getting data took'),
              (f'{int(t//60)} minutes, {int(t%60)} seconds.'))
    
    def plot(self, figsize_x=12, figsize_y=12, cmap='Set2'):

        _fig, ax = plt.subplots(figsize=(figsize_x,figsize_y))
        self.buildings.geometry.boundary.plot(color='k', linewidth=0.6, ax=ax)
        self.uprn.plot('street', ax=ax, markersize=5, cmap=cmap)
        self.roads.plot('id', ax=ax, linewidth=2, cmap=cmap)
        self.boundary.plot(ax=ax, linewidth=1.5, color='k')
        self.ax = ax

    def find_neighbours(self):
        
        self._neighbour = dict()
        # this probably just needs the right merge
        self._neighbour['streets'] = self.db.nearest_neighbours(
             'roadsnotsec', self.geom.buffer(1)
        )
        _streets = dict(zip(self._neighbour['streets'].UPRN, 
                            self._neighbour['streets'].id))
        self.uprn['street'] = self.uprn.UPRN.apply(
            lambda x: _streets.get(x))
    
    def tessellate(self):
        
        self.tiles = tessellate([
                self.roads, 
                gpd.GeoDataFrame(geometry=gpd.GeoSeries(
                    self.geom.boundary))
            ])
    
    def cellularize(self):
        self.cells = cellularize(self.uprn.geometry, self.geom)
