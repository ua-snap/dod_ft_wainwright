# 1951-2010 long term average CRU40

# ### NOTES:
# - CRU-TS40 data appear to have more strong features on the landscape, even when compared with adjacent CRU40 and 5ModelAvg future scenarios. 
# 	- Therefore, I think to have a spatial output that construes change through time and space, best thing to do would be to make a long-term average of the CRU-TS40 data for 1951-2010, and then do a difference between this baseline average and the future predictions (both processes will be run decadally).

import rasterio
import numpy as np
import xarray as xr
import os, glob

cru_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/SNAP_TEST_GIPL/freeze_to_thaw_length_cru40.tif'
ar5_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/SNAP_TEST_GIPL/freeze_to_thaw_length_decadal.tif'
output_filename = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/SNAP_TEST_GIPL/freeze_to_thaw_length_decadal_diff_cru_lta.tif'

cru = rasterio.open(cru_fn).read()
ar5 = rasterio.open(ar5_fn).read()

ar5[ ar5 == -9998 ] = np.nan # set the unsolvable to nan for the time being.

cru = cru.astype(np.float32)
cru[cru == -9998] = np.nan
cru_lta = np.rint( np.nanmean( cru, axis=0 ) )

ar5_deltas = np.array([ (cru_lta - arr) for arr in ar5 ])
_ = [np.place(arr,ar5[0] == -9999, -9999) for arr in ar5_deltas ] # update the mask

# set the np.nan to zero? I really need to think this through and clean up this codebase.
ar5_deltas[np.isnan(ar5_deltas)] = 0

with rasterio.open( ar5_fn ) as tmp:
	meta = tmp.meta.copy()
	meta.update(compress='lzw', count=ar5_deltas.shape[0])

with rasterio.open( output_filename, 'w', **meta ) as out:
	out.write( ar5_deltas.astype(np.float32) )


