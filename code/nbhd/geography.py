'''Geographical analysis.'''

from time import time
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
        
    def get_data(self, roads=True, uprn=True, buildings=True,
                 rail=False, rivers=False):
        
        t0 = time()
        
        if roads:
            self.roads = self.db.contains('openroads', self.geom.wkt)
        if uprn:
            self.uprn = self.db.contains('openuprn', self.geom.wkt)
        if buildings:
            self.buildings = self.db.contains('openmaplocal', self.geom.wkt)
        if rail:
            self.rail = self.db.contains('railways', self.geom.wkt)
        if rivers:
            self.rivers = self.db.contains('rivers', self.geom.wkt)
            
        t1 = time()
        t = t1 - t0
        print(f'Getting data took {t//60} minutes, {t%60} seconds.')
    
    def find_neighbours():
        pass