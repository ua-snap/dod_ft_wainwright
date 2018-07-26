# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# compute the decadal average of the annual frozen season length outputs.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

if __name__ == '__main__':
    import rasterio, os, glob
    import xarray as xr
    import numpy as np
    import pandas as pd
    import argparse
        
    parser = argparse.ArgumentParser( description='compute the frozen season length using thawOut_Day / freezeUp_Day outputs from the GIPL model -- DOD Ft.Wainwright project.' )
    parser.add_argument( '-fn', '--fn', action='store', dest='fn', type=str, help='path to annual frozen_length NetCDF file to use in decadal averaging.' )
    parser.add_argument( '-tfn', '--template_fn', action='store', dest='template_fn', type=str, help='path to the template GTiff file to use for file metadata' )
    parser.add_argument( '-o', '--out_path', action='store', dest='out_path', type=str, help='path to folder where the file(s) will be output. Extension will be dropped and .nc or .tif added to those flavors of outputs' )

    args = parser.parse_args()
    
    fn = args.fn
    template_fn = args.template_fn
    out_path = args.out_path

    if 'cru40' in fn:
        begin, end = '1960', '2009'
        b,e = '1960', '2000'
    else:
        begin, end = '2020', '2099'
        b,e = '2020', '2090'

    ds = xr.open_dataset( fn )
    variable = 'frozen_length'
    basename = '_'.join(os.path.basename( fn ).split('.')[0].split('_')[:-1])+'_decadal_{}-{}'.format(b,e)
    output_filename = os.path.join( out_path, basename )
    
    # make decadal
    ds_sel = ds.sel( time=slice( str(begin), str(end)) ).astype( np.float32 )
    ds_dec = ds_sel[ variable ].resample( time='10AS' ).mean( axis=0 ).round( 0 ).sel( time=slice(b,e) )

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



# # # # # EXAMPLE RUN
# import subprocess, os, glob

# path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length'
# out_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length/decadal'
# files = glob.glob(os.path.join( path, '*.nc' ))

# # the template is a raw file from the GIPL data delivery to use for metadata...
# template_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP45/ALT_Freeze_Thaw_Days_TIF/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp45_1km_ak_Interior_2016.tif'

# for fn in files:
#     _ = subprocess.call(['ipython','compute_decadals_from_frozen_season_length', '-fn', fn, '-tfn', template_fn, '-o', out_path])

