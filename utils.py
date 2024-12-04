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
    
def get_ndvi(start, end, bbox):
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,)
    search = catalog.search(
        collections = ['landsat-c2-l2'],
        bbox = bbox,
        query=["eo:cloud_cover<5"],
        datetime = start[0] + "/" + end[0]
    )
    items = search.get_all_items()
    len(items)
    print(items[2])
    for item in items:
        print(item.assets.keys())
        break

    stack = stackstac.stack(items, assets=["swir16", "red", "lwir"], epsg = 4326, bounds_latlon=bbox)
    B3 = stack.sel(band = "red")
    B4 = stack.sel(band = "swir16")
    LST = stack.sel(band = "lwir")
    ndvi = (B4 - B3) / (B3 + B4)
    return ndvi

def split_seasons(years, data):
    
    for i in years:
        if i == 0:
            year = years[i]
            spring_avg = average(data.sel(time=slice(f"{year}-03-21", f"{year}-06-21")))
            summer_avg = average(data.sel(time=slice(f"{year}-06-21", f"{year}-09-23")))
            fall_avg = average(data.sel(time=slice(f"{year}-09-23", f"{year}-12-22")))
            winter1 = data.sel(time=slice(f"{year}-12-22", f"{year}-12-31"))
            winter2 = data.sel(time=slice(f"{year}-01-01", f"{year}-03-20"))
            winter_avg = average(xr.concat([winter1, winter2], dim="time"))

        else:
            spring_avg = xr.concat([spring_avg, average(data.sel(time=slice(f"{year}-03-21", f"{year}-06-21")))], dim="time")
            summer_avg = xr.concat(xr.average(data.sel(time=slice(f"{year}-06-21", f"{year}-09-23"))), dim ="time")
            fall_avg = xr.concat(average(data.sel(time=slice(f"{year}-09-23", f"{year}-12-22"))), dim="time")
            winter1 = data.sel(time=slice(f"{year}-12-22", f"{year}-12-31"))
            winter2 = data.sel(time=slice(f"{year}-01-01", f"{year}-03-20"))
            winter_avg = xr.concat(average(xr.concat([winter1, winter2], dim="time")), dim="time")

    return spring_avg, summer_avg, fall_avg, winter_avg
    




