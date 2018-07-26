# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# compute the decadal average of the annual frozen season length outputs.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def compute_mean( arr ):
    ''' deal with nans in the means this needs solving but is not mission critical'''
    return np.rint( np.nanmean(arr, axis=0) )

if __name__ == '__main__':
    import rasterio, os, glob
    import xarray as xr
    import numpy as np
    import pandas as pd

    path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length'
    out_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length/decadal'
    files = glob.glob(os.path.join( path, '*.nc' ))

    # the template is a raw file from the GIPL data delivery to use for metadata...
    template_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP45/ALT_Freeze_Thaw_Days_TIF/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp45_1km_ak_Interior_2016.tif'

    for fn in files:
        if 'cru40' in fn:
            begin, end = '1960', '2009'
            b,e = '1960', '2000'
        else:
            begin, end = '2020', '2099'
            b,e = '2020', '2090'

        ds = xr.open_dataset( fn )
        variable = 'frozen_length'
        basename = os.path.basename( fn ).split('.')[0]+'_decadal_{}-{}'.format(b,e)
        output_filename = os.path.join( out_path, basename )
        
        # make decadal
        ds_sel = ds.sel( time=slice( str(begin), str(end)) ).astype(np.float32)
    
        ds_dec = ds_sel[ variable ].resample( time='10AS' ).mean( axis=0 ).round( 0 ).sel( time=slice(b,e) )
        # dec_means = np.array([ compute_mean( ds_sel[variable].isel( time=j ).data ) for i,j in ds_dec.groups.items() ])
        # ds_dec = ds_dec.mean(axis=0).sel(time=slice(b,e))
        # ds_dec.data = dec_means # update it with the proper np.nanmean outputs

        # write to a NetCDF
        ds_dec = ds_dec.to_dataset()
       
        # update global attrs
        ds_dec.attrs = {'name':'frozen_length',
                    'description':'number of days of frozen season,  which is determined by frozen at 0.5m and at 0.5cm depths',
                    'units':'days',
                    'crs':'EPSG:3338', 
                    'time step':'decadal mean'}

        ds_dec.to_netcdf( output_filename + '.nc', mode='w', format='NETCDF4' )

        # write to a GTiff
        with rasterio.open( template_fn ) as tmp:
            meta = tmp.meta.copy()
            meta.update( compress='lzw', count=ds_dec[variable].shape[0], dtype='float32' )
        
        with rasterio.open( output_filename + '.tif', 'w', **meta ) as out:
            out.write( ds_dec[variable].data.astype( np.float32 ) )
