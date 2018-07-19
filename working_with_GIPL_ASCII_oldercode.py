# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# working with the ASCII data... From GIPL -- DOD Ft. Wainwright -- June 2018
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def open_fn( fn ):
	return pd.read_csv( fn, sep='\s+' )

def open_daily_ascii( files, ncores=16 ):
	import multiprocessing as mp
	pool = mp.Pool(ncores)
	out = pool.map( open_fn, files )
	pool.close()
	pool.join()
	return out

if __name__ == '__main__':
	import os, glob
	import pandas as pd
	import geopandas as gpd
	from shapely.geometry import Point

	path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP85/Daily_Temperature_ASCII'
	wildcard = '' # 'thawOut_Day'
	output_filename = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/shapefiles/gipl2f_soil_temp_daily_ar5_5modelAvg_rcp85_1km_ak_Interior_4326.shp'

	files = sorted( glob.glob( os.path.join( path, '*{}*.txt'.format(wildcard) ) ) )
	years = [ int(fn.split('.')[0].split('_')[-1]) for fn in files ]
	fn_lookup = dict(zip(years, files))

	year = 2031
	df = pd.read_csv( fn_lookup[ year ], sep='\s+' )

