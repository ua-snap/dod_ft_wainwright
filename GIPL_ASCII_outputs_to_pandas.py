# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# working with the ASCII data... From GIPL -- DOD Ft. Wainwright -- June 2018
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

import os, glob
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP85/ALT_Freeze_Thaw_Days_ASCII'
wildcard = 'thawOut_Day'
output_filename = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/shapefiles/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp85_1km_ak_Interior_EPSG4326.shp'

files = sorted(glob.glob( os.path.join( path, '*{}*.txt'.format(wildcard) ) ) )

df = pd.concat([ pd.read_csv( fn, sep='\s+', header=None, names=[int(os.path.basename(fn).split('.')[0].split('_')[-1])] ) for fn in files ], axis=1 )

grid = pd.read_csv( '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP85/ALT_Freeze_Thaw_Days_ASCII/spatial_Grid_ak_Interior_11942.csv' )
grid['geometry'] = grid.apply( lambda x: Point(x.Lon,x.Lat), axis=1 )
gdf = gpd.GeoDataFrame( grid, geometry='geometry', crs={'init':'epsg:4326'} )
gdf.to_file( '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/shapefiles/grid_GIPL.shp' )

# make them a single GeoDataFrame
spat_df = gdf.join( df )
spat_df.columns = spat_df.columns.astype(str)
spat_df.to_file( output_filename )
# write it out to a shapefile

spat_df = spat_df.to_crs( epsg=3338 )
spat_df.to_file( '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/shapefiles/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp85_1km_ak_Interior_EPSG3338.shp' )


# GIPL OUTPUTS FILE METADATA
# In [4]: fn
# Out[4]: '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP85/ALT_Freeze_Thaw_Days_TIF/gipl2f_ALT_ar5_5modelAvg_rcp85_1km_ak_Interior_2006.tif'

# In [5]: rasterio.open(fn).meta
# Out[5]: 
# {'count': 1,
#  'crs': CRS({'lat_2': 65, 'no_defs': True, 'lat_0': 50, 'proj': 'aea', 'lon_0': -154, 'units': 'm', 'datum': 'NAD83', 'x_0': 0, 'lat_1': 55, 'y_0': 0}),
#  'driver': 'GTiff',
#  'dtype': 'float32',
#  'height': 178,
#  'nodata': -3.4028234663852886e+38,
#  'transform': Affine(1405.7926586248545, 0.0, 238665.2006927797,
#        0.0, -1405.792658624854, 1735181.9530677628),
#  'width': 180}




