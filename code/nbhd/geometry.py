'''
Some geometric functions.
''' 

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from scipy.spatial import Voronoi
from shapely.geometry import LineString, MultiLineString
from shapely.ops import polygonize, split


def tessellate(border_gdf_list):
    'Return tessellations from list of borders in geodataframes.'

    borders = pd.concat(border_gdf_list)
    borderlines = borders.unary_union
    polygons = polygonize(borderlines)
    tessellation = gpd.array.from_shapely(list(polygons),
                                        crs=27700)
    return gpd.GeoDataFrame(geometry=tessellation)

        
def cellularize(pts_geoseries, polygon):
    'Return geodataframe of Voronoi cells for points in polygon.'
    
    points = np.array([[p.x, p.y] for p in pts_geoseries])

    vor = Voronoi(points) 
    lines = [
        LineString(vor.vertices[line])
        for line in vor.ridge_vertices
    ]
    
    lines_gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(lines))
    lines_gdf.geometry = lines_gdf.geometry.apply(
        lambda x: MultiLineString([line for line
                                in list(split(x, polygon.boundary))
                                if polygon.buffer(1).contains(line)
                               ]))
    boundary_gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(polygon.boundary))
    cells_gdf = tessellate([boundary_gdf, lines_gdf])
    
    return cells_gdf
