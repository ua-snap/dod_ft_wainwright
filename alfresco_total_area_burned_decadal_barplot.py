import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
import os, glob
import pandas as pd
import numpy as np


path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/alfresco/total_area_burned'
wildcard = '5km'
l = [ fn for fn in glob.glob(os.path.join(path,'*{}*.csv'.format(wildcard))) if not 'historical' in fn ]

scenarios = ['rcp45', 'rcp60', 'rcp85']
files = { scenario:[ fn for fn in l if scenario in fn ]for scenario in scenarios }

# make a 5ModelAvg of the modeled outputs
modelavg = pd.DataFrame({ scenario:(sum([ pd.read_csv(fn, index_col=0) for fn in files[scenario] ]) / len(files)).mean(axis=1).round(0) for scenario in scenarios })
decades = [ i[:-1]+'0s' for i in modelavg.index.astype( str ) ]
decadals = modelavg.groupby( decades ).mean().round( 0 )

# [TODO] error bars? --> std does NOT work.
# stdev = modelavg.groupby( decades ).std()['1960s':'2050s']

# slice up the input data to the decades we are interested in
df = decadals['2010s':'2050s']
historical_df = decadals['1960s':'2000s']
historical_df = historical_df.iloc[:,0].to_frame(name='historical')

# put it back together and plot it
# fig, ax = plt.subplots()
plt.rcParams["figure.figsize"] = [16,9]
new_df = pd.concat( [historical_df, df], sort=True )
ax = new_df.plot( kind='bar' ) #, yerr=stdev)
begin = new_df.index[0]
end = new_df.index[-1]
# mess around with uneven tick spacing to make it look a bit better
locs = ax.xaxis.get_ticklocs()
new_locs = [ i-0.2 for i in locs[:5] ] + list(locs[5:])
ax.xaxis.set_ticks(new_locs)
plt.ylabel('Area Burned (km2)')
plt.title('ALFRESCO Decadal Mean Area Burned Estimates\n  mean across 200 replicates and 5 models \n {} buffer'.format(wildcard))

# [TODO]: add in a way to make the bars closer together? --> this may involve something like digging back into the raw axes and moving
# 			things around as we need them...  I will have to dig into this deeper, it may involve removing 'empty' bar rectangles thrown in 
# 			by pandas.
output_filename = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/alfresco/plots/tab_5ModelAvg_decadal/total_area_burned_decadal_means_5ModelAvg_{}_{}-{}.png'.format(wildcard, begin, end)
plt.savefig( output_filename )
plt.close()