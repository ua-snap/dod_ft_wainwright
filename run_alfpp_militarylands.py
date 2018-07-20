# * * * * * * * * * * * * * * * * * * * * * * * * * * *
# ALFRESCO POST-PROCESSING EXAMPLE 
# * * * * * * * * * * * * * * * * * * * * * * * * * * *

import alfresco_postprocessing as ap
import os, itertools
import argparse
	
parser = argparse.ArgumentParser( description='compute the ALF-PP over the domains for the DOD Project with Nancy' )
parser.add_argument( '-m', '--model', action='store', dest='model', type=str, help='modelname' )
parser.add_argument( '-s', '--scenario', action='store', dest='scenario', type=str, help='scenario name' )
args = parser.parse_args()

model = args.model
scenario = args.scenario

print( '{}-{}'.format(model, scenario) )

# # input args
ncores = 32
base_path = '/atlas_scratch/apbennett/IEM_AR5' # alfresco output maps dir
historical_maps_path = '/Data/Base_Data/ALFRESCO/AK_CAN_ALF_fires_geotiffs/files'
subdomains_fn = '/workspace/Shared/Users/malindgren/TEST_NANCY_DOD/InstallationBdry_buffered.shp'
id_field = 'id'
name_field = 'name'
# output_path = '/workspace/Shared/Users/malindgren/TEST_NANCY_DOD/alfresco'
output_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/alfresco'
obs_json_fn = os.path.join( output_path, 'historical_observed.json' )
metrics = [ 'veg_counts','avg_fire_size','number_of_fires','all_fire_sizes','total_area_burned','severity_counts' ]

historical fire input gtiffs -- RUN ONCE
pp_hist = ap.run_postprocessing_historical( historical_maps_path, obs_json_fn, ncores, ap.veg_name_dict, subdomains_fn, id_field, name_field)
metrics = [ 'avg_fire_size','number_of_fires','all_fire_sizes','total_area_burned' ]
out = ap.to_csvs( pp_hist, metrics, output_path, 'historical_observed', observed=True )
pp_hist.close()
# maps_path=historical_maps_path; out_json_fn=obs_json_fn; ncores=32; veg_name_dict=ap.veg_name_dict; subdomains_fn=subdomains_fn; id_field='id'; name_field='name'; background_value=0 

# run
curdirname = '{}_{}'.format(model, scenario)
mod_json_fn = os.path.join( output_path, '{}.json'.format(curdirname) )
suffix = curdirname # some id for the output csvs
maps_path = os.path.join( base_path, curdirname, 'Maps' )

# PostProcess
alfresco output gtiffs
pp = ap.run_postprocessing( maps_path, mod_json_fn, ncores, ap.veg_name_dict, subdomains_fn, id_field, name_field, lagfire=False )

# CSVs
# modeled
out = ap.to_csvs( pp, metrics, output_path, suffix, observed=False )
pp.close() # close the database

# * * * * * * * * PLOTTING * * * * * * * * * * * * * * * * * * * * * * * * * *
# build plot objects for comparison plots
modplot = ap.Plot( mod_json_fn, model=model, scenario=scenario )
obsplot = ap.Plot( obs_json_fn, model='historical', scenario='observed' )

# annual area burned barplot
replicate = 0
ap.aab_barplot_factory( modplot, obsplot, output_path, replicate, year_range=(1950, 2010) )

# veg counts lineplots
ap.vegcounts_lineplot_factory( modplot, output_path, replicate, year_range=(1950, 2100))

# annual area burned lineplots
ap.aab_lineplot_factory( modplot, obsplot, output_path, replicates=None, year_range=(1950, 2100) )


# # SOME TESTING AAB LINES
# obs_json_fn = 'historical_observed.json'
# mod_json_fn = 'IPSL-CM5A-LR_rcp45.json'
# model = 'IPSL-CM5A-LR'
# scenario = 'rcp45'
# output_path = '/workspace/Shared/Users/malindgren/TEST_NANCY_DOD/alfresco'

# modplot = ap.Plot( mod_json_fn, model=model, scenario=scenario )
# obsplot = ap.Plot( obs_json_fn, model='historical', scenario='observed' )

# ap.aab_lineplot_factory( modplot, obsplot, output_path, model, scenario, replicates=[None], year_range=(1950, 2100) )


	
