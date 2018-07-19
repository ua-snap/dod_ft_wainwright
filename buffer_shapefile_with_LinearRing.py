# make a buffered shapefile
from shapely.geometry import Polygon, LinearRing, MultiPolygon
from shapely.ops import cascaded_union, snap
import geopandas as gpd
from scipy.ndimage import label, generate_binary_structure
import rasterio
from rasterio.features import rasterize, shapes
from scipy.ndimage import label

# input shapefile of the installation boundaries and a template raster extent from ALF
shp_fn = '/workspace/Shared/Tech_Projects/DOD_Ft_Wainwright/project_data/shapefiles/FWA-DTA_GISfiles/InstallationBdry.shp'
template_fn = '/atlas_scratch/apbennett/IEM_AR5/GFDL-CM3_rcp45/Maps/1901/FireScar_1_1901.tif'

# pull some data from a template raster file to use in fixing the oddities in the shapefile topology
template_rst = rasterio.open( template_fn )
template_rst.crs.to_string()
crs = template_rst.crs.to_string()
gdf = gpd.read_file( shp_fn ).to_crs( crs )

# cascaded_union
union_pols = cascaded_union( MultiPolygon( list(gdf.geometry) ) )
out = gpd.GeoDataFrame({'id':[1],'geometry':[union_pols]}, geometry='geometry', crs=crs)

# rasterize to the ALF raster res/crs to overcome some issues with bad polygon topology
new_rst = rasterize( union_pols, out_shape=template_rst.shape, fill=0, default_value=1, transform=template_rst.transform )

meta = template_rst.meta.copy()
meta.update( compress='lzw', count=1, nodata=0 )

# label connected regions
new_arr,numfeatures = label(new_rst)

# write out the new shapefile of these newly 'fixed' polygons
out_shapes = [ Polygon(i['coordinates'][0]) for i,j in shapes(new_arr, transform=meta['transform']) if j > 0 ]
new_df = gpd.GeoDataFrame( {'id':list(range(len(out_shapes))), 'geometry':out_shapes}, crs=crs, geometry='geometry' )

# buffer all polygons
buf5 = new_df.buffer( 5000 )

# dissolve to a single multipolygon layer to deal with overlaps
buf5_dissolved = cascaded_union( list(buf5.geometry) )
buf5_df = gpd.GeoDataFrame( {'id':[1], 'geometry':[buf5_dissolved]}, geometry='geometry', crs=crs)

# buffer from 5km to 20km
buf20 = buf5_df.buffer( 15000 ) # 20km but we are performing from the 5km buffer

# dissolve to a single multipolygon to deal with overlaps and remove the 5km buffer + original polygons
buf20_dissolved = cascaded_union( list(buf20.geometry) )
buf20_dissolved_ring = Polygon( buf20_dissolved.exterior, [LinearRing(i.exterior.coords) for i in buf5_dissolved])

# add in buffer rings to 5km
overlaps_buf5 = { count:[ j for j in new_df.geometry if i.intersects(j)] for count,i in enumerate(buf5_dissolved) }
overlaps_buf5_ring = [ Polygon(list(buf5_dissolved)[ind].exterior, [LinearRing(i.exterior.coords) for i in pols ] ) for ind, pols in overlaps_buf5.items()]

all_shapes = overlaps_buf5_ring + [buf20_dissolved_ring] + list(new_df.geometry)
all_ids = [ 'buffer_5km' for i in overlaps_buf5_ring ] + ['buffer_20km'] + ['InstallationBdry' for i in list(new_df.geometry)]

buffered_df = gpd.GeoDataFrame( {'id':[i+1 for i in range(len(all_ids))], 'name':all_ids, 'geometry':all_shapes}, geometry='geometry', crs=crs)
# fix the id column:
for count, idx in enumerate([ np.where(buffered_df['name']==i)[0] for i in buffered_df.name.unique().tolist()]):
	buffered_df.loc[idx,'id'] = count+1
# dump to shapefile on disk
buffered_df.to_file( '/workspace/Shared/Users/malindgren/TEST_NANCY_DOD/InstallationBdry_buffered.shp' )

