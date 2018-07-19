# make a mask showing places that have all zeros or at least some zeros in the series.
import rasterio
import numpy as np

fn = freeze_fn # thaw_fn
ds = xr.open_dataset( fn )
a = ds.freezeUp_Day.data
all_zero = np.apply_along_axis( lambda x: (x == 0).all(), axis=0, arr=a ) 
some_zero = np.apply_along_axis( lambda x: len(np.where(x == 0)[0]) != 0 and len(np.where(x == 0)[0]) < len(x) , axis=0, arr=a )



