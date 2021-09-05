'''
Simplify the process of downloading and extracting Ordnance Survey data.
'''

import zipfile

import fiona
import pandas as pd
import geopandas as gpd
import requests


class OSDownloader():

    def __init__(self, download_immediately=True,
                 api_url='https://api.os.uk/downloads/v1/products'):

        response = requests.get(api_url)
        products = pd.DataFrame(response.json())
        products['download'] = products.url.apply(lambda x: requests.get(x).json()['downloadsUrl'])
        # products['download2'] = products.download.apply(lambda x: requests.get(x).json())
        products['formats'] = products.download2.apply(lambda x: [e['format'] for e in x])
        products['geopackage'] = products.formats.apply(lambda x: 'GeoPackage' in x)
        products['geopackage_url'] = products.apply(lambda x: [e['url'] for e in x.download2 
                                                               if e['format'] == 'GeoPackage'][0] 
                                                    if x.geopackage else None, axis=1)

        def download_row(row, _format):
            print(row.id)
            try:
                [url] = [e['url'] for e in row.download2 if e['format'].split(' ')[-1] == _format]
                with open(f'../data/{row.id}{_format}.zip', 'wb') as downloading:
                    downloading.write(requests.get(url).content)
                    downloading.close()
                return "Done!"
            except Exception as e:
                print(e)

        products['downloaded'] = products.apply(
            lambda x: download_row(x, 'GeoPackage') if x.geopackage\
            else download_row(x, 'Shapefile'), 
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
