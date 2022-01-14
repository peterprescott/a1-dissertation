import time

from multiprocessing import Pool

import sys
sys.path.append('..')

import pandas as pd

from nbhd import data
from nbhd.geography import get_communities


db = data.Base()
pixels = db.select('pixels')
       
def find_communities(pixel_row):
    print(f'Finding communities for {pixel_row[1]}')
    df, _ = get_communities(db, pixel_row[0])
    pixel_roads = df.loc[~df.roads_id.duplicated()]
    pixel_roads.columns
    pdf = pixel_roads[['roads_id','community','street_counts',
                       'street_length_per_uprn', 'footprint_area_per_uprn']]
    pdf['pixel'] = pixel_row[1]
    pdf['community'] = pdf.pixel + '_' + pdf.community
    pdf['time'] = time.ctime()
    pdf.columns = ['id', 'community', 'properties', 
                   'length_per_property', 'footprint_per_property', 'pixel', 'time']
    pdf.to_sql('faceblocks', db.engine, if_exists='append',index=False)
    return

if __name__=='__main__':
    
    with Pool(18) as p:
        p.map(find_communities, pixels.values)
