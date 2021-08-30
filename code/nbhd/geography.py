'''Geographical analysis.'''

from time import time

import matplotlib.pyplot as plt
from shapely.geometry import (Point,
                              LineString,
                              Polygon, 
                              MultiPolygon)


from .data import Base


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
        
        msg = 'Need to call `Neighbourhood.get_data()!'
        
        self.roads = msg
        self.uprn = msg
        self.buildings = msg
        
        self.rail = msg
        self.rivers = msg
        
    def get_data(self, wanted=('roads', 'uprn', 'buildings'), silent=True):
        
        t0 = time()
        
        table = {'roads': 'openroads',
                  'uprn': 'openuprn',
                  'buildings': 'openmaplocal',
                  'rail': 'railways',
                  'rivers': 'rivers'}
        
        for w in wanted:
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
    
    def find_neighbours():
        pass