# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# plot decadal frozen season length for each Installation boundary in the study region.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def get_mean_installbounds( arr, boundary_mask, boundary_groups ):
    return {boundary_groups[i]:np.mean(arr[boundary_mask == i]).round(0) for i in np.unique(boundary_mask[boundary_mask > 0])}
# function to round the number
def round( n ):
 
    # Smaller multiple
    a = (n // 10) * 10
     
    # Larger multiple
    b = a + 10
     
    # Return of closest of two
    return (b if n - a > b - n else a)

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
    data_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length/decadal'
    cru_fn = os.path.join( data_path, 'gipl2f_frozen_length_5cm_cru40_1km_ak_Interior_decadal.nc' )
    ar5_fn = os.path.join( data_path, 'gipl2f_frozen_length_5cm_ar5_5modelAvg_rcp{}_1km_ak_Interior_decadal.nc' )
    rcps = ['45','85']
    output_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/plots'
    variable = 'frozen_length'

    # do the cru-specific stuff first
    cru = xr.open_dataset( cru_fn ).sel( time=slice('1960','2000'))

    for rcp in rcps:
        ar5 = xr.open_dataset( ar5_fn.format( rcp ) ).sel( time=slice('2020','2090'))
        ds = xr.concat([cru.copy(deep=True),ar5], dim='time')
        
        # make raster mask using the InstallationBoundary shapefile
        shp_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/shapefiles/InstallationBoundary_SNAP_modified.shp'
        df = gpd.read_file( shp_fn )
        df = df.to_crs( meta['crs'].to_string() )
        shapes = [ (i,int(j))for i,j in zip(df.geometry.tolist(), df.facilityNu.tolist()) ]
        boundary_mask = rasterize( shapes, out_shape=tmp.shape, fill=0, transform=meta['transform'], all_touched=False )

        boundary_groups = {1:'FtWainwright', 2:'EielsonYC', 3:'Donnelly', 4:'Gerstle', 5:'BRapids_Whistler'}

        # make a df with the data we want to plot
        out_df = pd.DataFrame({ pd.Timestamp(sub_ds.time.data).year:get_mean_installbounds( sub_ds.data, boundary_mask, boundary_groups ) for sub_ds in ds[variable] })
        out_df[2010] = np.nan # since we have no 2010s decade...
        out_df = out_df[ sorted(out_df.columns) ]

        minvalue = out_df.T.loc[2020:2090].min().min() - 5

        # make a graphic that shows the decadals in each of the boundary_mask's
        ax = out_df.T.plot( kind='line', title='Frozen Period Length (days)' )
        ax.set_xlabel( 'Decade' )
        ax.set_ylabel( 'Days' )
        ax.hlines(80, xmin=1960, xmax=2000, capstyle='butt' )
        ax.text(1980, 76, 'CRU Historical', ha='center', va='center')
        ax.hlines(minvalue, xmin=2020, xmax=2090, capstyle='butt' )
        ax.text(2050, minvalue-4, 'CMIP5 Future (RCP{})'.format(rcp), ha='center', va='center')
        ymin,ymax = ax.get_ylim()
        # deal with the lower limit of the plot and the ar5 modeled description being a tad too low.
        if minvalue-20 < 0:
            ymin = 0
        else:
            ymin=minvalue-20
        
        ax.set_ylim( ymin, ymax )
        plt.savefig( os.path.join( output_path, 'freeze_to_thaw_length_decadal_lineplot_rcp{}.png'.format(rcp) ) )
        plt.close()

