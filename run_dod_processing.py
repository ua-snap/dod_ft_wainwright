# run all pre-processing

# # RUN STACKING
import subprocess, os

prefix_lu = {'thawOut_Day':'gipl2f_thawOut_Day_5cm','freezeUp_Day':'gipl2f_freezeUp_Day_0.5m','ALT':'gipl2f_ALT'}
out_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/gipl_netcdf'
for group in ['cru40', 'ar5_5modelAvg_rcp45', 'ar5_5modelAvg_rcp85']:
    if group in ['cru40','ar5_5modelAvg_rcp45']:
        rcp=45
    else:
        rcp=85
    if group == 'cru40':
        b,e = 1951, 2015
    else:
        b,e = 2016, 2099

    path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP{}/ALT_Freeze_Thaw_Days_TIF'.format(rcp)
    for variable in ['thawOut_Day', 'freezeUp_Day', 'ALT']:
        print( variable )
        output_filename = os.path.join( out_path, '_'.join([prefix_lu[variable],group,'1km_ak_Interior_{}-{}.nc'.format(b,e)]))
        os.chdir( '/workspace/UA/malindgren/repos/dod_ft_wainwright' )
        _ = subprocess.call(['python','stack_GIPL_outputs_to_NetCDF.py','-p', path, '-v', variable, '-g', group, '-o', output_filename, '-b', str(b), '-e', str(e) ])
        print('completed: {} '.format(output_filename))


# # RUN FROZEN LENGTH
import os, subprocess, glob

path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/gipl_netcdf'
out_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length'
groups = ['cru40','rcp85', 'rcp45']
variables = ['thawOut_Day', 'freezeUp_Day']
for group in groups:
    print( 'running: {}'.format( group ) )
    files = glob.glob( os.path.join( path, '*{}*.nc'.format(group) ) )
    files = { variable:fn for fn in files for variable in variables if variable in fn }
    new_fn = os.path.basename( files['thawOut_Day'] ).replace('thawOut_Day', 'frozen_length')
    output_filename = os.path.join( out_path, new_fn )
    os.chdir( '/workspace/UA/malindgren/repos/dod_ft_wainwright' )
    _ = subprocess.call([ 'python','compute_frozen_season_length.py','-t',files['thawOut_Day'],'-f',files['freezeUp_Day'],'-o',output_filename ])


# # COMPUTE DECADAL FROZEN LENGTH
import subprocess, os, glob

path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length'
out_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/frozen_season_length/decadal'
template_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP45/ALT_Freeze_Thaw_Days_TIF/gipl2f_thawOut_Day_5cm_ar5_5modelAvg_rcp45_1km_ak_Interior_2016.tif'
files = glob.glob(os.path.join( path, '*.nc' ))

for fn in files:
    os.chdir( '/workspace/UA/malindgren/repos/dod_ft_wainwright' )
    _ = subprocess.call(['python', 'compute_decadals_from_frozen_season_length.py', '-fn', fn, '-tfn', template_fn, '-o', out_path])


# # MAKE LONG-TERM AVG OF CRU40
import subprocess
os.chdir( '/workspace/UA/malindgren/repos/dod_ft_wainwright' )
_ = subprocess.call(['python','compute_long-term-avg_cru40_frozen_season_length.py'])


# # COMPUTE DIFFS FROM BASELINE LTA FOR RCP45/85
import subprocess
os.chdir( '/workspace/UA/malindgren/repos/dod_ft_wainwright' )
_ = subprocess.call(['python','compute_diffs_cru40_ar5_5ModelAvg_GIPL.py'])

# # CLASSIFY THE DIFF OUTPUTS FOR PLOTTING (?)
import subprocess
os.chdir( '/workspace/UA/malindgren/repos/dod_ft_wainwright' )
_ = subprocess.call(['python','classify_diffs_cru40_ar5_5ModelAvg_GIPL.py'])


