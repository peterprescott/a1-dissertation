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
from .utils import my_timer


class Neighbourhood:
    '''
    Theoretically-informed and data-driven neighbourhood analysis.
    '''

    def __init__(self, point=Point(338157,393037), db=Base()):
        '''Begin with a point on the British National Grid.'''
        
        self.db = db
        # find enclosure from database
        
        enclosures = db.within('enclosures', 0, point.x, point.y)
        if len(enclosures) == 1:
            self.geom = enclosures.geometry[0]
        else:
            print('boundary point!')
            self.geom = MultiPolygon(
                list(enclosures.geometry))
        
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
            setattr(self, w, self.db.contains(table[w], self.geom.wkt))
        
        t1 = time()
        t = t1 - t0
        print(('Getting data took'),
              (f'{int(t//60)} minutes, {int(t%60)} seconds.'))
    
    def plot(self, figsize_x=12, figsize_y=12, cmap='Set2'):
        
        _fig, self.ax = plt.subplots(figsize=(figsize_x,figsize_y))
        self.roads.plot(ax=self.ax)
        self.buildings.plot(ax=self.ax, color='lightgray')
        self.uprn.plot(ax=self.ax, color='black')
    
    def find_neighbours(self):
        
        self._neighbour = dict()
        self._neighbour['streets'] = self.db.nearest_neighbours(
            'openuprn', 'openroads', self.geom
        )
        _streets = dict(zip(self._neighbour['streets'].UPRN, 
                            self._neighbour['streets'].street_id))
        self.uprn['street'] = self.uprn.UPRN.apply(
            lambda x: _streets[x])
    
    def tessellate(self):
        
        self.tessellation = Tessellation([
                self.roads, 
                gpd.GeoDataFrame(geometry=gpd.GeoSeries(
                    self.geom.boundary))
            ])

class StreetNetwork():
    '''
    A spatial network is a graph in geometric space.
    '''
    pass

class FaceBlock():
    '''
    A face-block includes all of the dwellings
    that front on the same segment of the same street
    between any two intersections. [@RGrannis2009:p.31].
    '''
    
    def __init__(self, street_id: str, nbhd: Neighbourhood):
        pass
    
class VoronoiCells():
    '''
    Use Voronoi algorithm to divide space between points.
    '''
    def __init__(self, points):
        vor = Voronoi(points)
        lines = [
            LineString(vor.vertices[line])
            for line in vor.ridge_vertices
            if -1 not in line
        ]
        self.cells = polygonize(lines)

class Tessellation():
    '''
    A tessellation covers a plane with adjacent tiles with no gaps. 
    '''
    
    def __init__(self, border_gdf_list, color=True):
        'Requires a list of GeoDataFrames.'
        
        # assume everything has same CRS
        crs = border_gdf_list[0].crs 
        
        borders = pd.concat(border_gdf_list)
        borderlines = borders.unary_union
        polygons = polygonize(borderlines)
        tessellation = gpd.array.from_shapely(list(polygons),
                                            crs=crs)
        self.df = gpd.GeoDataFrame(geometry=tessellation)
        if color:
            self.df['c'] = greedy(self.df)
            subplot = self.df.plot('c', cmap='binary')
            self.figure = subplot.figure
        
        