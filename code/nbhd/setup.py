import zipfile

import fiona
import geopandas as gpd

class ZippedGpkg():
    
    def __init__(self, filepath):
        self.zf = zipfile.ZipFile(filepath)
        self.namelist = self.zf.namelist()
        [self.gpkg] = [f for f in self.namelist 
                       if f.split('.')[-1] == 'gpkg']
        self.layers = fiona.listlayers(self.zf.open(self.gpkg))
        self.unpacked = dict()
    
    def unpack(self, layername):
        self.unpacked[layername] = gpd.read_file(
            self.zf.open(self.gpkg), driver='GPKG', layer=layername)
        