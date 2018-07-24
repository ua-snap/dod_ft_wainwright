# frozen season length.
# time between frozen start and thaw start

def convert_ordinalday_year_to_datetime( year, ordinal_day ):
    '''
    ordinal_day = [int] range(1, 365+1) or range(1, 366+1) # if leapyear
    year = [int] four digit date that can be read in datetime.date
    '''
    from datetime import date, timedelta
    return date( year=year, month=1, day=1 ) + timedelta( ordinal_day - 1 )


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
    from functools import partial
    import datetime

    thaw_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp85_1km_ak_Interior_EPSG3338.nc'
    freeze_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/gipl2f_freezeUp_Day_0.5m_ar5_5modelAvg_rcp85_1km_ak_Interior_EPSG3338.nc'
    
    template_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP85/ALT_Freeze_Thaw_Days_TIF/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp85_1km_ak_Interior_2016.tif'
    with rasterio.open( template_fn ) as tmp:
        meta = tmp.meta.copy()
        meta.update( compress='lzw', nodata=-9999, count=1 )

    # make raster mask using the InstallationBoundary shapefile
    shp_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/shapefiles/InstallationBoundary_SNAP_modified.shp'
    df = gpd.read_file( shp_fn )
    df = df.to_crs( meta['crs'].to_string() )
    shapes = [ (i,int(j))for i,j in zip(df.geometry.tolist(), df.facilityNu.tolist()) ]
    boundary_mask = rasterize( shapes, out_shape=tmp.shape, fill=0, transform=meta['transform'], all_touched=False )

    boundary_groups = {1:'FtWainwright', 2:'EielsonYC', 3:'Donnelly', 4:'Gerstle', 5:'BRapids_Whistler'}

    variable = 'freezeUp_Day'
    begin, end = '2010','2099'

    thaw_ds = xr.open_dataset( thaw_fn )
    freeze_ds = xr.open_dataset( freeze_fn )

    thaw = thaw_ds.thawOut_Day.data
    freeze = freeze_ds.freezeUp_Day.data


def freeze_length_days( td, fd, tdyear, fdyear ):
    tdd = convert_ordinalday_year_to_datetime( tdyear, np.float(td) )
    fdd = convert_ordinalday_year_to_datetime( fdyear, np.float(fd) )
    return (tdd - fdd).days

out_arr = np.copy( thaw ) # we lose a timestep at the end by doing this sort of computation
out_arr[ out_arr != -9999 ] = -9998

years = [i.year for i in thaw_ds.time.to_index()]

# freeze lessthan thaw
ind = np.where((freeze < thaw) & (freeze != -9999) & (freeze != 0) & (thaw != 0) ) # --> use same year for time diff
for i,j,k in zip(*ind):
    out_arr[ i,j,k ] = freeze_length_days( thaw[i,j,k], freeze[i,j,k], years[i], years[i] )

# freeze is zero --> NO FREEZE to 0.5m -- make these values 0
ind = np.where((freeze == 0) & (thaw != 0) ) 
out_arr[ ind ] = 0

# use year+1 for thaw year for proper daycount using datetime.date
ind = np.where((freeze > thaw) & (freeze != -9999) & (freeze != 0) & (thaw != 0)) 
for i,j,k in zip(*ind):
    out_arr[ i,j,k ] = freeze_length_days( thaw[i,j,k], freeze[i,j,k], years[i]+1, years[i] )

meta['count'] = out_arr.shape[0]
with rasterio.open('/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/SNAP_TEST_GIPL/freeze_to_thaw_length.tif', 'w', **meta ) as out:
    out.write( out_arr.astype( np.int32 ) )

# make decadal
out_ds = freeze_ds.freezeUp_Day.copy( deep=True )
out_ds = out_ds.to_dataset( 'freezeUp_length' )
out_ds.freezeUp_length.data = out_arr

out_ds = out_ds.sel(time=slice('2020','2090'))
out_ds_dec = out_ds.freezeUp_length.resample( time='10A' ).mean( axis=0 )

meta['count'] = out_ds_dec.shape[0]
with rasterio.open('/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/SNAP_TEST_GIPL/freeze_to_thaw_length_decadal.tif', 'w', **meta ) as out:
    out.write( out_ds_dec.data.astype( np.int32 ) )

# make a graphic that shows the decadals in each of the boundary_mask's
def get_mean_installbounds( arr, boundary_mask, boundary_groups ):
    return {boundary_groups[i]:np.mean(arr[boundary_mask == i]).round(0) for i in np.unique(boundary_mask[boundary_mask > 0])}

# f = partial( get_mean_installbounds, boundary_mask=boundary_mask )
out_df = pd.DataFrame({ pd.Timestamp(sub_ds.time.data).year:get_mean_installbounds( sub_ds.data, boundary_mask, boundary_groups ) for sub_ds in out_ds_dec })

ax = out_df.T.plot( kind='line', title='Frozen Period Length (days)' )
ax.set_xlabel( 'Decade' )
ax.set_ylabel( 'Days' )
plt.savefig( '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/plots_July2018/freeze_to_thaw_length_decadal.png' )
plt.close()

# # not in our region lookups below, but may be still necessary:
# np.where((freeze != 0) & (thaw == 0)& (boundary_mask > 0)) # thaw is zero --> NO THAW of TOP LAYER --> [NOTE]: not in our region
# np.where((freeze == 0) & (thaw == 0)& (boundary_mask > 0)) # both are zero --> [NOTE]: not in our region

meta['count'] = freeze_ds.freezeUp_Day.shape[0]
with rasterio.open('/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/SNAP_TEST_GIPL/freeze_dates.tif', 'w', **meta ) as out:
    out.write( freeze_ds.freezeUp_Day.data.astype( np.int32 ) )

meta['count'] = thaw_ds.thawOut_Day.shape[0]
with rasterio.open('/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/SNAP_TEST_GIPL/thaw_dates.tif', 'w', **meta ) as out:
    out.write( thaw_ds.thawOut_Day.data.astype( np.int32 ) )

