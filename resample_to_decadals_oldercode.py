def resample_to_decadals( fn ):
    ds = xr.open_dataset( fn )
    ds_sel = ds.sel( time=slice('2010','2099') )
    # decades = [ int(str(x.year)[:3]+'0') for x in ds_sel.time.to_pandas().index ]
    ds_dec_mean = ds_sel.resample(time='10A', closed='left', label='left').mean().round(0).astype(np.int32)
    return ds_dec_mean.sel( time=slice('2010','2099') )


if __name__ == '__main__':
    import matplotlib
    matplotlib.use('agg')
    from matplotlib import pyplot as plt
    import rasterio
    import geopandas as gpd
    from rasterio.features import rasterize
    import xarray as xr
    import pandas as pd
    import numpy as np

    thaw_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp85_1km_ak_Interior_EPSG3338.nc'
    freeze_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/gipl2f_freezeUp_Day_0.5m_ar5_5modelAvg_rcp85_1km_ak_Interior_EPSG3338.nc'
    
    #  make decadals and slice to the full decades
    thaw_dec = resample_to_decadals( thaw_fn )
    freeze_dec = resample_to_decadals( freeze_fn )

    # # get some template raster information from Sergeys GTiff outputs he sent
    # with rasterio.open( files[0] ) as tmp:
    #     meta = tmp.meta.copy()
    #     meta.update( compress='lzw', nodata=-9999, count=10 )

    # for decade,arr in zip(np.unique(decades),ds_dec_mean.thawOut_Day.data):
    #     # output_filename = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/decadals/thawOut_Day/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp85_1km_ak_Interior_{}.tif'.format(decade)
    #     output_filename = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/decadals/thawOut_Day/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp85_1km_ak_Interior_multiband.tif'.format(decade)
    #     with rasterio.open( output_filename, 'w', **meta ) as out:
    #         # out.write( arr, 1 )
    #         out.write( ds_dec_mean.thawOut_Day.data )


    # # baseline is 2010...  its the best we can really do
    # baseline = ds_dec_mean.thawOut_Day.data[0,...]
    # arr_2030 = ds_dec_mean.thawOut_Day.data[2,...]
    # arr_2050 = ds_dec_mean.thawOut_Day.data[4,...]

    # diff_2030 = baseline - arr_2030
    # diff_2030[ baseline == -9999 ] = -9999

    # diff_2050 = baseline - arr_2050
    # diff_2050[ baseline == -9999 ] = -9999

    template_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP85/ALT_Freeze_Thaw_Days_TIF/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp85_1km_ak_Interior_2006.tif'
    with rasterio.open( template_fn ) as tmp:
        meta = tmp.meta.copy()
        meta.update( compress='lzw', nodata=-9999, count=1 )

    # output_filename = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/decadals/thawOut_Day/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp85_1km_ak_Interior_2010_2030_DIFF.tif'
    # with rasterio.open( output_filename, 'w', **meta ) as out:
    #     # out.write( arr, 1 )
    #     out.write( diff_2030, 1 )

    # output_filename = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/decadals/thawOut_Day/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp85_1km_ak_Interior_2010_2050_DIFF.tif'
    # with rasterio.open( output_filename, 'w', **meta ) as out:
    #     # out.write( arr, 1 )
    #     out.write( diff_2050, 1 )


    # make raster mask using the InstallationBoundary shapefile
    shp_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/shapefiles/InstallationBoundary_SNAP_modified.shp'
    df = gpd.read_file( shp_fn )
    df = df.to_crs( meta['crs'].to_string() )
    shapes = [ (i,int(j))for i,j in zip(df.geometry.tolist(), df.facilityNu.tolist()) ]
    boundary_mask = rasterize( shapes, out_shape=tmp.shape, fill=0, transform=meta['transform'], all_touched=False )

    boundary_groups = {1:'Ft.Wainwright', 2:'Eielson/YC', 3:'Donnelly', 4:'Gerstle', 5:'Black Rapids/Whistler'}

    # average the data within the masked area (installations) by decade
    thawOut_Day_decadal_mean = dict()
    freezeUp_Day_decadal_mean = dict()
    for i in sorted(list(boundary_groups.keys())):
        rows, cols = np.where( boundary_mask == i )
        thawOut_Day_decadal_mean['{}'.format(boundary_groups[i])] = thaw_dec.thawOut_Day.values[:,rows, cols].mean(axis=1).astype(np.int32)
        freezeUp_Day_decadal_mean['{}'.format(boundary_groups[i])] = freeze_dec.freezeUp_Day.values[:,rows, cols].mean(axis=1).astype(np.int32)

    # # combine the dicts
    # data = {**thawOut_Day_decadal_mean, **freezeUp_Day_decadal_mean}

    # plot freeze
    plot_df = pd.DataFrame( freezeUp_Day_decadal_mean, index=range(2010,2090+1,10) )
    plot_df.plot( kind='line' )
    plt.savefig( '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/plots/freezedate_decadal_separate_installations_rcp85.png' )
    plt.close()

    # plot thaw
    plot_df = pd.DataFrame( thawOut_Day_decadal_mean, index=range(2010,2090+1,10) )
    plot_df.plot( kind='line' )
    plt.savefig( '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/plots/thawdate_decadal_separate_installations_rcp85.png' )
    plt.close()


