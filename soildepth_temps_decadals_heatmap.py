# # # MAKE PROFILE DEPTH HEATMAP PLOT -- DOD Ft.Wainwright -- June 2018

def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero

    Input
    -----
      cmap : The matplotlib colormap to be altered
      start : Offset from lowest point in the colormap's range.
          Defaults to 0.0 (no lower ofset). Should be between
          0.0 and `midpoint`.
      midpoint : The new center of the colormap. Defaults to 
          0.5 (no shift). Should be between 0.0 and 1.0. In
          general, this should be  1 - vmax/(vmax + abs(vmin))
          For example if your data range from -15.0 to +5.0 and
          you want the center of the colormap at 0.0, `midpoint`
          should be set to  1 - 5/(5 + 15)) or 0.75
      stop : Offset from highets point in the colormap's range.
          Defaults to 1.0 (no upper ofset). Should be between
          `midpoint` and 1.0.
    '''
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False), 
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = matplotlib.colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap

def make_data( fn ):
	df = pd.read_csv( fn, sep='\s+' )
	# subset it to the points that are within the InstallationBoundaries
	df_bounds = df[ df.nPoint.isin( joined.id ) ]
	df_bounds = df_bounds.merge( jdf, left_on='nPoint', right_on='id' )

	# get the means of each of the areas
	return df_bounds.groupby(['facilityNu','Day']).mean()


if __name__ == '__main__':
	import matplotlib
	matplotlib.use('agg')
	from matplotlib import pyplot as plt
	from matplotlib import colors
	from mpl_toolkits.axes_grid1 import AxesGrid, make_axes_locatable
	import geopandas as gpd
	import pandas as pd
	import numpy as np
	from shapely.geometry import Point
	import os, glob
	import multiprocessing as mp
	import seaborn as sns

	rcps = ['45','85']
	# path where the GIPL ASCII outputs are stored.
	data_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP{}/Daily_Temperature_ASCII'
	output_path = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/SNAP_modified/plots'
	# boundary shapefile and grid shapefile
	shp_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/shapefiles/InstallationBoundary_SNAP_modified.shp'
	grid_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP85/ALT_Freeze_Thaw_Days_ASCII/spatial_Grid_ak_Interior_11942.csv'

	# open it up:
	crs = {'init':'epsg:3338'}
	boundaries = gpd.read_file( shp_fn ).to_crs( crs )
	boundaries = boundaries[['facilityNu', 'geometry']]
	grid = pd.read_csv( '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/GIPL/AR5_5modelAvg_RCP85/ALT_Freeze_Thaw_Days_ASCII/spatial_Grid_ak_Interior_11942.csv' )

	geom = grid.apply(lambda x: Point(x.Lon, x.Lat), axis=1)
	grid = gpd.GeoDataFrame( grid, geometry=geom, crs={'init':'epsg:4326'} ).to_crs( crs )

	# merge in the installation boundary id's
	joined = gpd.sjoin( grid, boundaries, how='inner', op='intersects' )
	jdf = joined[['id','facilityNu']].copy()
	jdf.loc[:,'facilityNu'] = jdf.loc[:,'facilityNu'].astype( int ) # update dtype

	# open the temperature dailies at depths csv for a single year
	# datacols =['0.00', '0.01', '0.02', '0.03', '0.04', '0.05', '0.10', '0.20', '0.30', '0.40', '0.50', '0.75', '1.00']
	datacols = ['0.00','0.10', '0.20', '0.30', '0.40', '0.50']
	boundary_groups = {1:'Ft.Wainwright', 2:'Eielson/YC', 3:'Donnelly', 4:'Gerstle', 5:'Black Rapids/Whistler'}

	for rcp in rcps:
		cur_path = data_path.format( rcp )

		decadal_means = dict()
		hold = []
		decades = range( 2020, 2051, 10 )
		for decade in decades:
			print( decade )
			files = sorted( glob.glob( os.path.join( cur_path, '*{}*.txt'.format( str(decade)[:3]) )))
			# make decadal averages using the above logic. -- hack pool below. its a mess.
			pool = mp.Pool( 32 )
			data = pool.map( make_data, files )
			pool.close()
			pool.join()
			df = (sum(data)/len(data))[ datacols ]
			df['decade'] = decade
			hold = hold + [df]

		def draw_heatmap(*args, **kwargs):
			data = kwargs.pop('data')
			d = data.pivot(index=args[1], columns=args[0], values=args[2])
			ax = sns.heatmap(d, **kwargs)
			# ax.vlines([297,24],0,13)

		df_dec = pd.concat( hold )
		melted = df_dec.reset_index().melt(['facilityNu','Day','decade'])
		for i in range(1,6,1):
			cur_data = melted[melted.facilityNu == i]
			vmax = cur_data.value.max().round(0)
			vmin = cur_data.value.min().round(0)
			# cmap = sns.diverging_palette(240, 10, center='light', as_cmap=True)

			midpoint = 1 - cur_data['value'].max()/(cur_data['value'].max() + abs(cur_data['value'].min()))
			cmap = shiftedColorMap(plt.get_cmap('RdBu_r'), midpoint=midpoint, name='RdBu_r_shifted')
			# cmap = shiftedColorMap(cmap, midpoint=0, name='RdYlBu_r_shifted')
			colnames = cur_data.columns
			cur_data.columns = [ i if not 'variable' in i else 'depth (m)' for i in colnames ]

			with sns.plotting_context( font_scale=2 ):
				# sns.set( font_scale=1.1 )
				fg = sns.FacetGrid( cur_data, row='decade', height=4, aspect=3, sharey=True ) # changed size to height
				g = fg.map_dataframe( draw_heatmap, 'Day', 'depth (m)', 'value', cbar=True, square=False, cmap=cmap, vmin=vmin, vmax=vmax )
				
				title_font_dict = {'fontsize': 15,
								'fontweight' : 'normal',
								'verticalalignment': 'baseline',
								'horizontalalignment': 'center'}

				for ax, title in zip( g.axes.flat, [ str(dec)+'s' for dec in decades ] ):
					ax.set_title( title, title_font_dict )

				# build the proper spacing for the begin/middle/end of months
				xticks = []
				month_days = [31,28,31,30,31,30,31,31,30,31,30,31]
				for idx,ii in enumerate(month_days):
					if idx > 0:
						x = x2 + (ii/2)
						x1 = x - (ii/2)
						x2 = x + (ii/2)
					else:
						x = ii/2
						x1 = 0
						x2 = x1+ii

					xticks = xticks + [x1,x,x2]

				xticks = sorted(list(set(xticks)))
		
				g.set( xlim=(min(xticks), max(xticks)), xticks=np.array(xticks) )
				months = ['','Jan','','Feb','','Mar','', 'Apr','', 'May', '', 'Jun', '', 'Jul', '', 'Aug','', 'Sep', '', 'Oct', '', 'Nov', '', 'Dec', '' ]
				g.set_xticklabels( months, rotation=0 )
				
				plt.savefig(os.path.join( output_path, 'soildepth_heatmap_decades_rcp{}_{}_{}-{}.png'.format(rcp,''.join(e for e in boundary_groups[i] if e.isalnum()), str(decades[0])+'s', str(decades[-1])+'s') ))
				plt.close()
