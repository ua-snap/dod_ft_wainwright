 def jd_to_date(jd):
    """
    Convert Julian Day to date.
    
    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 
        4th ed., Duffet-Smith and Zwart, 2011.
    
    Parameters
    ----------
    jd : float
        Julian Day
        
    Returns
    -------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.
        
    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.
    
    day : float
        Day, may contain fractional part.
        
    Examples
    --------
    Convert Julian Day 2446113.75 to year, month, and day.
    
    >>> jd_to_date(2446113.75)
    (1985, 2, 17.25)
    
    """
    import math

    jd = jd + 0.5
    
    F, I = math.modf(jd)
    I = int(I)
    A = math.trunc((I - 1867216.25)/36524.25)
    
    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I
        
    C = B + 1524
    D = math.trunc((C - 122.1) / 365.25)
    E = math.trunc(365.25 * D)
    G = math.trunc((C - E) / 30.6001)
    
    day = C - E + F - math.trunc(30.6001 * G)
    
    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
        
    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715
        
    return year, month, day
    
def date_to_jd(year,month,day):
    """
    Convert a date to Julian Day.
    
    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 
        4th ed., Duffet-Smith and Zwart, 2011.
    
    Parameters
    ----------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.
        
    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.
    
    day : float
        Day, may contain fractional part.
    
    Returns
    -------
    jd : float
        Julian Day
        
    Examples
    --------
    Convert 6 a.m., February 17, 1985 to Julian Day
    
    >>> date_to_jd(1985,2,17.25)
    2446113.75
    
    """
    import math

    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    
    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
        (year == 1582 and month < 10) or
        (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)
        
    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)
        
    D = math.trunc(30.6001 * (monthp + 1))
    jd = B + C + D + day + 1720994.5
    
    return jd

def convert_to_julian_date( days, year ):
    dt_days = [datetime.fromordinal(d) for d in days]
    out = [ date_to_jd( year, dt.month, dt.day ) for dt in dt_days ]
    return out

def run_year( arr, year ):
    arr = arr.astype( np.float32 )
    f = partial( convert_to_julian_date, year=year )
    ind = np.where( arr > 0 )
    arr[ ind ] = np.apply_along_axis( f, arr=arr[ ind ], axis=0 )
    return arr

def convert_GIPL_ordinal_to_jd( fn, variable, output_filename ):
    ''' function to actually run the conversion of the netcdfs SNAP made from GIPL FreezeUp/ThawOut GTiffs'''
    ds = xr.open_dataset( fn )
    groups = ds[ variable ].groupby( 'time.year' )

    new_arr = np.array([ run_year( group.data[0,...], gname ) for gname, group in groups ])
    ds[ variable ].data = new_arr

    # write the new NetCDF to disk
    ds.attrs.update({'units':'Julian Date -- 0 Julian date is noon January 1, 4713 BC'})
    ds[ variable ].encoding.update( dtype=np.float32, _FillValue=-9999 ) # update encodings for new dtype
    ds.to_netcdf( output_filename, mode='w', format='NETCDF4' )
    return output_filename


if __name__ == '__main__':
    from datetime import datetime
    import numpy as np
    import xarray as xr
    from functools import partial
    import rasterio

    # input netcdf files 
    thaw_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp85_1km_ak_Interior_EPSG3338.nc'
    freeze_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/gipl2f_freezeUp_Day_0.5m_ar5_5modelAvg_rcp85_1km_ak_Interior_EPSG3338.nc'
    fn_var_list = [(thaw_fn,'thawOut_Day'),(freeze_fn,'freezeUp_Day')]

    for fn, variable in fn_var_list:
        print( variable )
        output_filename = fn.replace('.nc', '_jdate.nc')
        done = convert_GIPL_ordinal_to_jd( fn, variable, output_filename )
