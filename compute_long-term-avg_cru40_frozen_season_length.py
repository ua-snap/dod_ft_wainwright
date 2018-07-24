
def compute_mean( arr ):
    ''' deal with nans in the means this needs solving but is not mission critical'''
    return np.rint( np.nanmean(arr, axis=0) )

if __name__ == '__main__':
    import rasterio, os, glob
    import xarray as xr
    import numpy as np
    import pandas as pd

    fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length/gipl2f_frozen_length_5cm_cru40_1km_ak_Interior.nc'
    output_filename = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length/decadal/gipl2f_frozen_length_5cm_cru40_1km_ak_Interior_LTA'
    template_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP45/ALT_Freeze_Thaw_Days_TIF/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp45_1km_ak_Interior_2016.tif'
   	variable = 'frozen_length'
   	
   	ds = xr.open_dataset( fn )
   	arr = ds[ variable ].data
   	lta = compute_mean( arr )

   	with rasterio.open( template_fn ) as tmp:
   		meta = tmp.meta.copy()
   		meta.update( compress='lzw', count=1 )

   	# GTiff
   	with rasterio.open( output_filename + '.tif', 'w', **meta ) as out:
   		out.write( lta )

 	# netcdf4
 	new_ds = ds.copy( deep=True )
 	new_ds = new_ds.isel( time=0 )
 	new_ds[variable].data = lta
 	new_ds.to_netcdf( output_filename + '.nc', mode='w', format='NETCDF4' )