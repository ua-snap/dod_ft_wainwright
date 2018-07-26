# 1951-2010 long term average CRU40

# ### NOTES:
# - CRU-TS40 data appear to have more strong features on the landscape, even when compared with adjacent CRU40 and 5ModelAvg future scenarios. 
# 	- Therefore, I think to have a spatial output that construes change through time and space, best thing to do would be to make a long-term average of the CRU-TS40 data for 1951-2010, and then do a difference between this baseline average and the future predictions (both processes will be run decadally).

import rasterio
import numpy as np
import xarray as xr
import os, glob

rcps = ['rcp45','rcp85']
cru_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length/decadal/gipl2f_frozen_length_5cm_cru40_1km_ak_Interior_LTA_1951-2015.tif'
ar5_files = ['/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length/decadal/gipl2f_frozen_length_5cm_ar5_5modelAvg_{}_1km_ak_Interior_decadal_2020-2090.tif'.format(rcp) for rcp in rcps]
output_filenames = ['/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length/decadal_diff_from_baseline/freeze_to_thaw_length_decadal_diff_{}_cru_lta_2020-2090.tif'.format(rcp) for rcp in rcps]

cru_lta = rasterio.open( cru_fn ).read( 1 )
decades = list(range(2020,2091,10))
for ind, rcp in enumerate(rcps):
	ar5 = rasterio.open(ar5_files[ind]).read()
	
	ar5_deltas = np.array([ (cru_lta - arr) for arr in ar5 ])
	_ = [np.place(arr,ar5[0] == -9999, -9999) for arr in ar5_deltas ] # update the mask

	with rasterio.open( ar5_files[ind] ) as tmp:
		meta = tmp.meta.copy()
		meta.update( compress='lzw', count=ar5_deltas.shape[0], nodata=-9999 )

	with rasterio.open( output_filenames[ind], 'w', **meta ) as out:
		out.write( ar5_deltas.astype(np.float32) )

	for idx, decade in enumerate( decades ):
		out_fn = output_filenames[ind].replace('_2020-2090.tif', '_{}.tif'.format(decade))

		meta.update( count=1 )
		with rasterio.open( out_fn, 'w', **meta ) as out:
			out.write( ar5_deltas[idx].astype(np.float32), 1 )