# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#  classify diffs into numeric classes for mapping purposes.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

import os, glob
import rasterio
import numpy as np

fn = ''

bins = [-45,-30,-15,0,15,30,60]
with rasterio.open( fn ) as rst:
	arr = rst.read()
	new_arr = np.digitize( arr, bins=bins )
	new_arr[arr == -9999] = -9999

	meta = rst.meta.copy()
	meta.update( compress='lzw', dtype='int32' )

with rasterio.open( output_filename, 'w', **meta ) as out:
	out.write( new_arr.astype(np.int32) )