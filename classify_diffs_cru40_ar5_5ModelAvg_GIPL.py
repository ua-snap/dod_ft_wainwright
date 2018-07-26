# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#  classify diffs into numeric classes for mapping purposes.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

import os, glob
import rasterio
import numpy as np

path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length/decadal_diff_from_baseline'
files = [ fn for fn in glob.glob( os.path.join( path, '*.tif' ) ) if '_classified' not in fn and '2020-2090' in fn ]

for fn in files:
	dirname, basename = os.path.split( fn )
	print( 'classifying: {}'.format( basename ) )
	output_filename = os.path.join( dirname, basename.replace( '.tif', '_classified.tif' ) )

	bins = [-365,-45,-15,0,1,15,30,60,90,365]
	# 1<-45 
	# 2<-15
	# 3<0
	# 4<1 <- ZERO NO CHANGE
	# 5<15
	# 6<30
	# 7<60
	# 8<90
	# 9<365 <- FULL YEAR
	with rasterio.open( fn ) as rst:
		arr = rst.read()

		new_arr = np.digitize( arr, bins=bins, right=False ).astype(np.float32)
		new_arr[arr == -9999] = -9999
		
		meta = rst.meta.copy()
		meta.update( compress='lzw', dtype='float32', nodata=-9999 )

	with rasterio.open( output_filename, 'w', **meta ) as out:
		out.write( new_arr.astype( np.float32 ) )

	# dump out into individual rasters for ease of mapping
	for idx, decade in enumerate(list(range(2020,2091,10))):
		meta.update( count=1 )
		output_filename = os.path.join( dirname, basename.replace('2020-2090',str(decade)).replace( '.tif', '_classified.tif') )
		with rasterio.open( output_filename, 'w', **meta ) as out:
			out.write( new_arr[idx].astype( np.float32 ), 1 )
