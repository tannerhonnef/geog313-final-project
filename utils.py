import pystac_client
import planetary_computer
import leafmap
import geogif
import stackstac
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from avgNdwi import main
from scipy.stats import gaussian_kde

def average(dataArray):
    avgArray = dataArray.mean(dim=["time"], skipna=True)
    return avgArray


def get_bands(start, end, bbox):
    """
    This function takes in a spatial and temporal timeframe,
        and finds appropriate landast data from microsoft's planetary computer website.
    It then calculates ndvi as a new column within the fetched data, 
        and returns the full array.
    Inputs: 
    start = datetime object, representing the start of the time period of interest
    end = datetime object, representing the end of the time period of interest
    bbox = spatial bounding box
    Outputs:
    xarray.DataArray with ndvi data
    """
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,)
    search = catalog.search(
        collections = ['landsat-c2-l2'],
        bbox = bbox,
        query=["eo:cloud_cover<5"],
        datetime = start + "/" + end
    )
    items = search.get_all_items()
    # len(items)
    # print(items[2])
    # for item in items:
    #     print(item.assets.keys())
    #     break

    stack = stackstac.stack(items, assets=["nir08", "red", "lwir", "qa_pixel"], epsg = 4326, bounds_latlon=bbox)
    
    B3 = stackNoClouds.sel(band = "red")
    B4 = stackNoClouds.sel(band = "nir08")
    LST = stackNoClouds.sel(band = "lwir")
    B3 = B3.where(B3 > 0, np.nan)
    B4 = B4.where(B4 > 0, np.nan)
    ndvi = (B4 - B3) / (B4 + B3)


# https://docs.xarray.dev/en/stable/examples/monthly-means.html
def season_mean_dict(ds, calendar="standard"):
    # from xarray documentation example
    # Make a DataArray with the number of days in each month, size = len(time)
    month_length = ds.time.dt.days_in_month

    # Calculate the weights by grouping by 'time.season'
    weights = (
        month_length.groupby("time.season") / month_length.groupby("time.season").sum()
    )

    # Test that the sum of the weights for each season is 1.0
    np.testing.assert_allclose(weights.groupby("time.season").sum().values, np.ones(4))

    # Calculate the weighted average
    weighted_average = (ds * weights).groupby("time.season").sum(dim="time")

    
    # original code
    ordered_seasons = ['winter', 'summer', 'spring', 'fall']
    d = {}
    count = 0
    for season in weighted_average:
        d[ordered_seasons[count]] = season
        count += 1
    return d

def scatter_ndvi_lst(ndvi, lst):
    plt.rcParams['figure.figsize'] = (12,8)
    plt.figure(figsize = (5, 5))
    plt.scatter(x=ndvi, y=lst)
    plt.xlabel("NDVI")
    plt.ylabel("LST")
    plt.ylim(0,50)
    plt.xlim(-5,5)
    plt.show()
