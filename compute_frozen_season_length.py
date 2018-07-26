# # # # # # # # # # # # # # # # # # # # # # # #
# compute frozen season length.
# time between frozen start and thaw start
# # # # # # # # # # # # # # # # # # # # # # # #

def convert_ordinalday_year_to_datetime( year, ordinal_day ):
    '''
    ordinal_day = [int] range(1, 365+1) or range(1, 366+1) # if leapyear
    year = [int] four digit date that can be read in datetime.date
    '''
    from datetime import date, timedelta
    return date( year=year, month=1, day=1 ) + timedelta( ordinal_day - 1 )

def freeze_length_days( td, fd, tdyear, fdyear ):
    ''' count the number of days of the frozen season using datetime objects.'''
    tdd = convert_ordinalday_year_to_datetime( tdyear, np.float(td) )
    fdd = convert_ordinalday_year_to_datetime( fdyear, np.float(fd) )
    return (tdd - fdd).days

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
    import argparse
        
    parser = argparse.ArgumentParser( description='compute the frozen season length using thawOut_Day / freezeUp_Day outputs from the GIPL model -- DOD Ft.Wainwright project.' )
    parser.add_argument( '-t', '--thaw_fn', action='store', dest='thaw_fn', type=str, help='path to thawOut_Day SNAP-stacked NetCDF file' )
    parser.add_argument( '-f', '--freeze_fn', action='store', dest='freeze_fn', type=str, help='path to freezeUp_Day SNAP-stacked NetCDF file' )
    parser.add_argument( '-o', '--output_filename', action='store', dest='output_filename', type=str, help='path to netcdf file to be output.' )

    args = parser.parse_args()
    thaw_fn = args.thaw_fn
    freeze_fn = args.freeze_fn
    output_filename = args.output_filename

    # open the files
    thaw_ds = xr.open_dataset( thaw_fn )
    freeze_ds = xr.open_dataset( freeze_fn )

    # get the data arrays
    thaw = thaw_ds.thawOut_Day.data
    freeze = freeze_ds.freezeUp_Day.data

    # make an output array from one of the ones we are starting with
    out_arr = np.copy( thaw )
    out_arr[ out_arr != -9999 ] = -9998

    # make a year list from the index variable
    years = [i.year for i in thaw_ds.time.to_index()]

    # freeze lessthan thaw
    ind = np.where((freeze < thaw) & (freeze != -9999) & (freeze != 0) & (thaw != 0) ) # --> use same year for time diff
    for i,j,k in zip(*ind):
        out_arr[ i,j,k ] = freeze_length_days( thaw[i,j,k], freeze[i,j,k], years[i], years[i] )

    # freeze is zero --> NO FREEZE to 0.5m -- make these values 0
    ind = np.where((freeze == 0) & (thaw != 0) )
    out_arr[ ind ] = 0

    # [new] thaw is zero freeze > 0 --> never thawed...
    ind = np.where( (thaw == 0) & (freeze > 0) )
    # 365 - freezeday # (?)
    out_arr[ ind ] = 365 - freeze[ ind ]

    # [new] if both are zero --> never freeze and never thaw --> must be 365
    ind = np.where( (thaw == 0) & (freeze == 0))
    out_arr[ ind ] = 365

    # use year+1 for thaw year for proper daycount using datetime.date
    ind = np.where((freeze > thaw) & (freeze != -9999) & (freeze != 0) & (thaw != 0)) 
    for i,j,k in zip(*ind):
        out_arr[ i,j,k ] = freeze_length_days( thaw[i,j,k], freeze[i,j,k], years[i]+1, years[i] )

    # copy one of the input netcdf and fill it with the new data.
    da = thaw_ds.thawOut_Day.copy( deep=True )
    ds = da.to_dataset( name='frozen_length' )
    ds.frozen_length.data = out_arr

    # update global attrs
    ds.attrs = {'name':'frozen_length',
    'description':'number of days of frozen season,  which is determined by frozen at 0.5m and at 0.5cm depths',
    'units':'days',
    'crs':'EPSG:3338'}

    # dump to disk
    ds.to_netcdf( output_filename, mode='w', format='NETCDF4' )


# # # # # # # EXAMPLE RUN: # # # # # 
# import os, subprocess, glob

# path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/gipl_netcdf'
# out_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length'
# groups = ['cru40','rcp85', 'rcp45']
# variables = ['thawOut_Day', 'freezeUp_Day']
# for group in groups:
#     print( 'running: {}'.format( group ) )
#     files = glob.glob( os.path.join( path, '*{}*.nc'.format(group) ) )
#     files = { variable:fn for fn in files for variable in variables if variable in fn }
#     new_fn = os.path.basename( files['thawOut_Day'] ).replace('thawOut_Day', 'frozen_length')
#     output_filename = os.path.join( out_path, new_fn )
#     _ = subprocess.call([ 'python','compute_frozen_season_length.py','-t',files['thawOut_Day'],'-f',files['freezeUp_Day'],'-o',output_filename ])
# # # # # # # # # # # # # # # # # # 
