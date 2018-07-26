# # # # 
# make netcdf files from the GIPL output GeoTiffs -- DOD Ft.Wainwright June 2018
# # # # 

def open_raster( fn, band=1 ):
    with rasterio.open( fn ) as out:
        arr = out.read( band )
    return arr

def coordinates( fn=None, meta=None, numpy_array=None, input_crs=None, to_latlong=False ):
    '''
    take a raster file as input and return the centroid coords for each 
    of the grid cells as a pair of numpy 2d arrays (longitude, latitude)

    User must give either:
        fn = path to the rasterio readable raster
    OR
        meta & numpy ndarray (usually obtained by rasterio.open(fn).read( 1 )) 
        where:
        meta = a rasterio style metadata dictionary ( rasterio.open(fn).meta )
        numpy_array = 2d numpy array representing a raster described by the meta

    input_crs = rasterio style proj4 dict, example: { 'init':'epsg:3338' }
    to_latlong = boolean.  If True all coordinates will be returned as EPSG:4326
                         If False all coordinates will be returned in input_crs
    returns:
        meshgrid of longitudes and latitudes

    borrowed from here: https://gis.stackexchange.com/a/129857
    ''' 
    
    import rasterio
    import numpy as np
    from affine import Affine
    from pyproj import Proj, transform

    if fn:
        # Read raster
        with rasterio.open( fn ) as r:
            T0 = r.transform  # upper-left pixel corner affine transform
            p1 = Proj( r.crs )
            A = r.read( 1 )  # pixel values

    elif (meta is not None) & (numpy_array is not None):
        A = numpy_array
        if input_crs != None:
            p1 = Proj( input_crs )
            T0 = meta[ 'transform' ]
        else:
            p1 = None
            T0 = meta[ 'transform' ]
    else:
        BaseException( 'check inputs' )

    # All rows and columns
    cols, rows = np.meshgrid(np.arange(A.shape[1]), np.arange(A.shape[0]))
    # Get affine transform for pixel centres
    T1 = T0 * Affine.translation( 0.5, 0.5 )
    # Function to convert pixel row/column index (from 0) to easting/northing at centre
    rc2en = lambda r, c: ( c, r ) * T1
    # All eastings and northings -- this is much faster than np.apply_along_axis
    eastings, northings = np.vectorize(rc2en, otypes=[np.float, np.float])(rows, cols)

    if to_latlong == False:
        return eastings, northings
    elif (to_latlong == True) & (input_crs != None):
        # Project all longitudes, latitudes
        longs, lats = transform(p1, p1.to_latlong(), eastings, northings)
        return longs, lats
    else:
        BaseException( 'cant reproject to latlong without an input_crs' )

def make_nc( filenames, out_fn, variable, ncpus=32 ):
    
    pool = mp.Pool( ncpus )
    arr = np.array( pool.map( open_raster, files ) ).astype( np.int32 )
    arr[ arr < 0 ] = -9999
    pool.close()
    pool.join()

    # get the coordinates as a meshgrid
    x,y = coordinates( fn=files[0] )
    begin = os.path.splitext(files[0])[0].split('_')[-1]
    end = str(int(os.path.splitext(files[-1])[0].split('_')[-1]) + 1)
    time = pd.date_range( begin, end, freq='A' )

    new_ds = xr.Dataset({variable: (['time','yc','xc'], arr)},
                    coords={'xc': ('xc', x[0,]),
                            'yc': ('yc', y[:,0]),
                            'time':time })

    # write it back out to disk with compression encoding
    encoding = new_ds[ variable ].encoding
    encoding.update( zlib=True, complevel=5, contiguous=False, chunksizes=None, dtype='int32' )
    new_ds[ variable ].encoding = encoding
        
    # [TODO]: add attrs to the filename
    # - proj4string, metadata, etc...
    new_ds.attrs.update( proj4string=rasterio.open(files[0]).crs.to_string(), EPSG=3338 )
    
    # dump to disk
    new_ds.to_netcdf( out_fn, mode='w', format='NETCDF4' )
    return out_fn

if __name__ == '__main__':
    import xarray as xr
    import numpy as np
    import rasterio
    import os, glob
    import multiprocessing as mp
    import pandas as pd
    import argparse

    parser = argparse.ArgumentParser( description='stack GIPL model thawOut_Day / freezeUp_Day to NetCDF -- DOD Ft.Wainwright Project' )
    parser.add_argument( '-p', '--path', action='store', dest='path', type=str, help='path to the folder containing the GIPL GeoTiff files' )
    parser.add_argument( '-v', '--variable', action='store', dest='variable', type=str, help='variable name --> (typically) "thawOut_Day" / "freezeUp_Day"' )
    parser.add_argument( '-g', '--group', action='store', dest='group', type=str, help='group name --> (typically) "cru40" / "ar5_5modelAvg_rcp85" / "ar5_5modelAvg_rcp45"' )
    parser.add_argument( '-o', '--output_filename', action='store', dest='output_filename', type=str, help='full pathname of the output NetCDF4 file to be produced.' )
    args = parser.parse_args()

    # parse the args for ease of use
    path = args.path
    variable = args.variable
    group = args.group
    output_filename = args.output_filename

    files = sorted( glob.glob( os.path.join( path, '*{}*{}*.tif'.format(variable, group) ) ) )

    # stack them into a somewhat fleshed-out, but functional NetCDF file
    make_nc( files, output_filename, variable, ncpus=8 )



# # # # # # # # # # EXAMPLE RUN: # # # # # # # # 
# import subprocess, os
#
# prefix_lu = {'thawOut_Day':'gipl2f_thawOut_Day_5cm','freezeUp_Day':'gipl2f_freezeUp_Day_0.5m'}
# out_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/gipl_netcdf'
# for group in ['cru40', 'ar5_5modelAvg_rcp45', 'ar5_5modelAvg_rcp85']:
#     if group in ['cru40','ar5_5modelAvg_rcp45']:
#         rcp=45
#     else:
#         rcp=85        
#    
#     path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP{}/ALT_Freeze_Thaw_Days_TIF'.format(rcp)
#     for variable in ['thawOut_Day', 'freezeUp_Day', 'ALT']:
#         output_filename = os.path.join( out_path, '_'.join([prefix_lu[variable],group,'1km_ak_Interior.nc']))
#         _ = subprocess.call(['python','stack_GIPL_outputs_to_NetCDF.py','-p', path, '-v', variable, '-g', group, '-o', output_filename])
#         print('completed: {} '.format(output_filename))
# # # # # # # # # # # # # # # # # # # # # # # # #


