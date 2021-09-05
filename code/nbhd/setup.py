import os
import zipfile

import requests
import fiona
import pandas as pd
import geopandas as gpd



class OSDownloader():
    
    def __init__(self, api_url='https://api.os.uk/downloads/v1/products',
                       datafolder_path='data',
                       download_immediately=True):
        
        self.datafolder_path = datafolder_path
        if not os.path.exists(self.datafolder_path):
            os.mkdir(self.datafolder_path)
        
        print(f'Requesting data from {api_url}...')
        self.api_url = api_url
        self.response = requests.get(self.api_url)
        print('First request successful!')
        self.products = pd.DataFrame(self.response.json())
        print('Getting download links...')
        self.products['download'] = self.products.url.apply(
                    lambda x: requests.get(f'{x}/downloads').json())
        self.products['formats'] = self.products.download.apply(
                    lambda x: [e['format'] for e in x])
        self.products['geopackage'] = self.products.formats.apply(
                    lambda x: 'GeoPackage' in x)
        self.products['geopackage_url'] = self.products.apply(
                    lambda x: [e['url'] for e in x.download 
                                if e['format'] == 'GeoPackage'][0] 
                                if x.geopackage else None, 
                    axis=1)
        
        if download_immediately:
            self.download_all()
   
    def download_row(self, row, _format):
        
        try:
            print(f'Trying to download {row.id} in {_format} format...')
            [url] = [e['url'] for e in row.download 
                     if e['format'].split(' ')[-1] == _format]
            
            with open(os.path.join(self.datafolder_path, 
                                   f'{row.id}{_format}.zip')
                      , 'wb') as downloading:
                downloading.write(requests.get(url).content)
                downloading.close()
            print('Done!')
            return "Done!"
        except Exception as e:
            print(e)

    def download_all(self):
        print('Attempting downloads...')
        self.products['downloaded'] = self.products.apply(
            lambda x: self.download_row(x, 'GeoPackage') if x.geopackage\
            else self.download_row(x, 'Shapefile'), 
            axis=1
        )


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