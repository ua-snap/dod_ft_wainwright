# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# plot decadal frozen season length for each Installation boundary in the study region.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def get_mean_installbounds( arr, boundary_mask, boundary_groups ):
    return {boundary_groups[i]:np.mean(arr[boundary_mask == i]).round(0) for i in np.unique(boundary_mask[boundary_mask > 0])}

if __name__ == '__main__':
    import matplotlib
    matplotlib.use('agg')
    from matplotlib import pyplot as plt
    import os, rasterio
    from rasterio.features import rasterize
    import geopandas as gpd
    import xarray as xr
    import pandas as pd
    import numpy as np

    # read in the files we want to plot
    cru_fn = ''
    ar5_fn = ''
    cru = xr.open_dataset( cru_fn )
    ar5 = xr.open_dataset( ar5_fn )

    # make raster mask using the InstallationBoundary shapefile
    shp_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/shapefiles/InstallationBoundary_SNAP_modified.shp'
    df = gpd.read_file( shp_fn )
    df = df.to_crs( meta['crs'].to_string() )
    shapes = [ (i,int(j))for i,j in zip(df.geometry.tolist(), df.facilityNu.tolist()) ]
    boundary_mask = rasterize( shapes, out_shape=tmp.shape, fill=0, transform=meta['transform'], all_touched=False )

    boundary_groups = {1:'FtWainwright', 2:'EielsonYC', 3:'Donnelly', 4:'Gerstle', 5:'BRapids_Whistler'}

    years = [i.year for i in thaw_ds.time.to_index()]

    # make a df with the data we want to plot
    out_df = pd.DataFrame({ pd.Timestamp(sub_ds.time.data).year:get_mean_installbounds( sub_ds.data, boundary_mask, boundary_groups ) for sub_ds in out_ds_dec })

    # make a graphic that shows the decadals in each of the boundary_mask's
    ax = out_df.T.plot( kind='line', title='Frozen Period Length (days)' )
    ax.set_xlabel( 'Decade' )
    ax.set_ylabel( 'Days' )
    plt.savefig( '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/SNAP_TEST_GIPL/freeze_to_thaw_length_decadal.png' )
    plt.close()

