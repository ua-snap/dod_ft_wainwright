# RCP85 VERSION
def resample_to_decadals( fn, variable, boundary_mask, begin, end ):
    ds = xr.open_dataset( fn )
    ds_sel = ds.sel( time=slice(begin, end) )
    # ds_dec_mean = ds_sel.resample(time='10A', closed='left', label='left').mean().round(0).astype(np.float32)
    ds_dec_mean = ds_sel.resample(time='10A', closed='left', label='left')
    slices = ds_dec_mean.groups
    out = dict()
    for np_dt, sl in slices.items():
        bound_dict = dict()
        for i in np.unique( boundary_mask[ boundary_mask > 0 ] ):
            # testing...
            ds_slice = ds_sel.isel( time=sl )[ variable ].data
            masked = ds_slice[:, ((boundary_mask == i))]
            good_ind = np.where( masked > 0 )
            vals = masked[ good_ind ]
            # set all vals less than a value to that value + 365 for averaging
            vals[vals < 150] = vals[vals < 150] + 365
            mean_val = np.mean( vals )
            if mean_val > 365:
                new_mean_val_area_decade = np.rint( mean_val - 365 )
            else:
                new_mean_val_area_decade = np.rint( mean_val )
            
            bound_dict[ boundary_groups[i] ] = int(new_mean_val_area_decade)

        # end testing...
        out[ pd.Timestamp(np_dt).year ] = bound_dict

    return pd.DataFrame( out )


def compute_day_diffs( vals ):
    # set all vals less than a value to that value + 365 for averaging
    vals[ vals == 0 ] = np.nan
    vals[vals < 150] = vals[vals < 150] + 365
    mean_val = np.mean( vals )
    if mean_val > 365:
        new_mean_val_area_decade = np.rint( mean_val - 365 )
    else:
        new_mean_val_area_decade = np.rint( mean_val )
    return new_mean_val_area_decade


def compute_day_diffs_2( vals, year ):
    if not (vals == -9999).any():
        dt_list = [ convert_ordinalday_year_to_datetime( year+1, ordinal_day ) if ordinal_day < 150 else convert_ordinalday_year_to_datetime( year, ordinal_day ) for ordinal_day in vals.tolist() ]
        diff_days = [ (i-dt_list[0]).days for i in dt_list[1:] ]
        out_val = np.mean( diff_days ).round()
    else:
        out_val = -9999

    return out_val


def resample_to_decadals_ordinal_table( fn, variable, boundary_mask, begin, end ):
    ds = xr.open_dataset( fn )
    ds_sel = ds.sel( time=slice(begin, end) )
    # ds_dec_mean = ds_sel.resample(time='10A', closed='left', label='left').mean().round(0).astype(np.float32)
    ds_dec_mean = ds_sel.resample(time='10A', closed='left', label='left')
    slices = ds_dec_mean.groups

    out = dict()
    for np_dt, sl in slices.items():
        year = pd.Timestamp(np_dt).year
        ds_slice = ds_sel.isel( time=sl )[ variable ].copy().data
        dec_arr = np.apply_along_axis( compute_day_diffs, arr=ds_slice.copy(), axis=0 )
        dec_arr[ ds_slice[0] == -9999 ] = -9999 # update the mask

        masked_means = { i:compute_day_diffs( dec_arr[ (boundary_mask == i) & (dec_arr > 0) ] ) for i in np.unique( boundary_mask[ boundary_mask > 0 ] )}
        out[ year ] = masked_means

    return pd.DataFrame( out )

def resample_to_decadals_ordinal_GTiff( fn, out_path, variable, boundary_mask, begin, end, out_meta ):
    import os

    ds = xr.open_dataset( fn )
    ds_sel = ds.sel( time=slice(begin, end) )
    ds_dec_mean = ds_sel.resample(time='10A', closed='left', label='left')
    slices = ds_dec_mean.groups

    out = dict()
    for np_dt, sl in slices.items():
        year = pd.Timestamp(np_dt).year
        # filename-fu
        basename = os.path.basename( fn )
        basename, ext = os.path.splitext( basename )
        basename = '_'.join(basename.split( '_' )[:-1] + [str(year)])
        basename = basename + '_decadal_ordinal_avg' + '.tif'
        out_fn = os.path.join( out_path, basename )
        
        ds_slice = ds_sel.isel( time=sl )[ variable ].copy().data
        dec_arr = np.apply_along_axis( compute_day_diffs, arr=ds_slice.copy(), axis=0 )
        dec_arr[ ds_slice[0] == -9999 ] = -9999 # update the mask

        with rasterio.open( out_fn, 'w', **out_meta ) as out:
            out.write( dec_arr.astype(np.float32), 1 )

    return out_path

# vars for the above funcs
out_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/decadal_averages'
out_meta = meta


def resample_to_decadals_day_change( fn, variable, boundary_mask, begin, end ):
    ds = xr.open_dataset( fn )
    ds_sel = ds.sel( time=slice(begin, end) )
    # ds_dec_mean = ds_sel.resample(time='10A', closed='left', label='left').mean().round(0).astype(np.float32)
    ds_dec_mean = ds_sel.resample(time='10A', closed='left', label='left')
    slices = ds_dec_mean.groups

    out = dict()
    for np_dt, sl in slices.items():
        break
        year = pd.Timestamp(np_dt).year
        ds_slice = ds_sel.isel( time=sl )[ variable ].copy().data
        f = partial(compute_day_diffs_2, year=year)
        dec_arr = np.apply_along_axis( f, arr=ds_slice.copy(), axis=0 )
        # dec_arr[ ds_slice[0] == -9999 ] = -9999 # update the mask

        masked_means = { i:dec_arr[ (boundary_mask == i) & (dec_arr != -9999) ].mean() for i in np.unique( boundary_mask[ boundary_mask > 0 ] )}
        out[ year ] = masked_means

    return pd.DataFrame( out )


def convert_ordinalday_year_to_datetime( year, ordinal_day ):
    '''
    ordinal_day = [int] range(1, 365+1) or range(1, 366+1) # if leapyear
    year = [int] four digit date that can be read in datetime.date
    '''
    import datetime
    return datetime.date( year=year, month=1, day=1 ) + datetime.timedelta( ordinal_day - 1 )



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
    from datetime import date, datetime

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
    decadals = resample_to_decadals( freeze_fn, variable, boundary_mask, begin, end )

    # since the data averages using the other technique we conjured up in the meeting skew towards January, I am 
    # removing the values in the few series that lean December for plotting purposes
    decadals[decadals > 150] = (decadals[decadals > 150] - 365)
    decadals = decadals.abs() # get absolute value so we dont have negatives.

    # line plot it
    decadals.T.plot(kind='line')
    plt.savefig( '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/plots/freezedate_decadal_separate_installations_rcp85_mean_newmethod.png' )
    plt.close()

    # heatmap it
    arr = decadals.T.as_matrix()
    rownames = decadals.T.index
    colnames = decadals.T.columns

    midpoint = 1 - arr.max()/(arr.max() + abs(arr.min()))
    cmap = shiftedColorMap(plt.get_cmap('RdYlBu_r'), midpoint=midpoint, name='RdYlBu_r_shifted')

    # plot it
    fig = plt.figure()
    ax = fig.add_subplot( 111 )
    cax = ax.matshow( arr, cmap=cmap ) # interpolation='nearest', aspect='auto'

    plt.gca().xaxis.tick_bottom()

    # # ticks and labels
    # labels, locs = rownames.tolist(), rownames.astype(float).tolist()
    # plt.yticks(locs, labels)

    # labels, locs = colnames.tolist(), colnames.astype(float).tolist()
    # plt.xticks(labels,locs)


    # set a colorbar to the proper height
    divider = make_axes_locatable( ax )
    ccax = divider.append_axes( "right", size="5%", pad=0.05 )

    plt.colorbar( cax, orientation='vertical', cax=ccax )

    # ax.set_yticklabels( rownames[::2].tolist() )
    # ax.set_xticklabels(colnames)
    plt.tight_layout()
    # plt.xticks = colnames
    plt.savefig('/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/test_matshow_biweek_{}_{}.png'.format(boundary_groups[i].replace(' ', '').replace('/','').replace('.',''),decade), figsize=(9,11))
    plt.close()




    # average the data within the masked area (installations) by decade
    thawOut_Day_decadal_mean = dict()
    thawOut_Day_decadal_min = dict()
    thawOut_Day_decadal_max = dict()
    freezeUp_Day_decadal_mean = dict()
    freezeUp_Day_decadal_min = dict()
    freezeUp_Day_decadal_max = dict()
    for i in sorted(list(boundary_groups.keys())):
        rows, cols = np.where( boundary_mask == i )
        thawOut_Day_decadal_mean['{}'.format(boundary_groups[i])] = thaw_dec.thawOut_Day.values[:,rows, cols].mean(axis=1).astype(np.float32)
        # min/max
        thaw = thaw_dec.thawOut_Day.values[:,rows, cols]
        thawOut_Day_decadal_min['{}'.format(boundary_groups[i])] = np.array(np.ma.masked_where(thaw <= 0, thaw, copy=True).min(axis=1).astype(np.float32))
        thawOut_Day_decadal_max['{}'.format(boundary_groups[i])] = np.array(np.ma.masked_where(thaw <= 0, thaw, copy=True).max(axis=1).astype(np.float32))

        freezeUp_Day_decadal_mean['{}'.format(boundary_groups[i])] = freeze_dec.freezeUp_Day.values[:,rows, cols].mean(axis=1).astype(np.float32)
        # min/max
        freeze = freeze_dec.freezeUp_Day.values[:,rows, cols]
        freezeUp_Day_decadal_min['{}'.format(boundary_groups[i])] = np.array(np.ma.masked_where(freeze <= 0, freeze, copy=True).min(axis=1).astype(np.float32))
        freezeUp_Day_decadal_max['{}'.format(boundary_groups[i])] = np.array(np.ma.masked_where(freeze <= 0, freeze, copy=True).max(axis=1).astype(np.float32))
   
    # # combine the dicts
    # data = {**thawOut_Day_decadal_mean, **freezeUp_Day_decadal_mean}

    # plot freeze
    plot_df = pd.DataFrame( freezeUp_Day_decadal_min, index=range(2020,2090+1,10) )
    ax = plot_df.plot( kind='line' )
    # ax.fill_between( plot_df.index,freezeUp_Day_decadal_min['Donnelly'], freezeUp_Day_decadal_max['Donnelly'] )
    plt.savefig( '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/plots/freezedate_decadal_separate_installations_rcp85_min.png' )
    plt.close()

    # plot thaw
    plot_df = pd.DataFrame( thawOut_Day_decadal_min, index=range(2020,2090+1,10) )
    plot_df.plot( kind='line' )
    plt.savefig( '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/plots/thawdate_decadal_separate_installations_rcp85_min.png' )
    plt.close()


