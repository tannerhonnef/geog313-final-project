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

def get_bands(start, end, bbox, cloudcover):
    """
    This function takes in a spatial and temporal timeframe,
        and finds appropriate landast data from microsoft's planetary computer website.
    It then calculates ndvi as a new column within the fetched data, 
        and returns the full array.
    Inputs: 
    start = datetime object, representing the start of the time period of interest
    end = datetime object, representing the end of the time period of interest
    bbox = spatial bounding box
    cloudcover = int representing percent cloudcover
    Outputs:
    xarray.DataArray with ndvi data
    """
    # calling planetary computer to get data
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,)
    search = catalog.search(
        collections = ['landsat-c2-l2'],
        bbox = bbox,
        query={
        "eo:cloud_cover": {"lt": cloudcover},
        "platform": {"in": ["landsat-8", "landsat-9"]}
    },
        datetime = start + "/" + end
    )
    items = search.get_all_items()

    # creating a stack with the necessary bands for NDVI and LST calculation with qa_pixel for bitmasking
    stack = stackstac.stack(items, assets=["nir08", "red", "lwir11", "qa_pixel"], epsg = 4326, bounds_latlon=bbox)

    # bit masking clouds, cloud shadows, and water
    mask_bitfields = [1, 2, 3, 4, 7]
    bitmask = 0
    for field in mask_bitfields:
        bitmask |= 1 << field
    
    bin(bitmask)
    
    qa = stack.sel(band="qa_pixel").astype("uint16")
    mask = qa & bitmask
    
    stackNoClouds = stack.where(mask == 0)

    # calculating NDVI and converting LST to Celsius
    B3 = stackNoClouds.sel(band = "red")
    B4 = stackNoClouds.sel(band = "nir08")
    LST = stackNoClouds.sel(band = "lwir11")
    # removing zeros to reduce extraneous values
    B3 = B3.where(B3 > 0, np.nan)
    B4 = B4.where(B4 > 0, np.nan)
    ndvi = (B4 - B3) / (B4 + B3)

    LST = LST - 273.15

    return ndvi, LST

def season_mean_dict(ds):
    """
    This function takes a dataset and calculates the mean across time for each season.  
        The seasons are defined as:
        Winter: December, January, February
        Spring: March, April, May
        Summer: June, July, August
        Fall: September, October, November
    It first prints the number of scenes for each season.
    It outputs a dictionary with the key being the season and the value being the mean of all scenes in that season.
    Input: 
    ds = dataset representing LST or NDVI data
    Output:
    dictionary with the average NDVI for each pixel for each season
    seasonal keys: winter, spring, summer, fall
    """
    # grouping the data by season
    grouped = ds.groupby('time.season')
    d = {}

    # printing the number of images for each season
    print("There are", len(grouped["DJF"]), "scences for winter.")
    print("There are", len(grouped["MAM"]), "scences for spring.")
    print("There are", len(grouped["JJA"]), "scences for summer.")
    print("There are", len(grouped["SON"]), "scences for fall.")

    # creating a dictionary key and value for each season with the mean of the scenes for that season
    d["winter"] = grouped["DJF"].mean(dim=["time"], skipna=True)
    d["spring"] = grouped["MAM"].mean(dim=["time"], skipna=True)
    d["summer"] = grouped["JJA"].mean(dim=["time"], skipna=True)
    d["fall"] = grouped["SON"].mean(dim=["time"], skipna=True)
    
    return d

def createDensity(avgNdvi, avgLst, ax):
    """
    This function takes two dataarrays and generates a density plot with a dataarray on each axis.
    Input:
        avgNdvi: x-axis data
        avgLST: y-axis data
        ax: list with placement of plot
            [0,0] is the top left
            [1,1] is the bottom right
    Output:
    returns a density plot which is shown by the plot function below
    """
    # converting to numpy arrays
    avgLst = np.asarray(avgLst.values)
    avgNdvi = np.asarray(avgNdvi.values)

    # creating a mask
    valid_mask = ~np.isnan(avgLst) & ~np.isnan(avgNdvi)

    # applying mask and flatten
    avgLst = avgLst[valid_mask].flatten()
    avgNdvi = avgNdvi[valid_mask].flatten()

    # creating a histogram
    hist, xedges, yedges = np.histogram2d(avgNdvi, avgLst, bins=1000)

    # plotting the density on the given axes object
    im = ax.imshow(
        hist.T,
        origin='lower',
        aspect='auto',
        extent=[xedges.min(), xedges.max(), yedges.min(), yedges.max()],
        cmap='Blues',
        vmax=20
    )

    # labeling
    ax.set_xlabel("NDVI")
    ax.set_ylabel("LST (Degrees Celsius)")
    return im

def plot(avgNdvi, avgLST):
    """
    This function takes two dictionaries with 4 dataarrays each and calls the 
        createDensity function to create a density plot for each pair of arrays.
    Input:
        avgNdvi: dictionary of x-axis data
        avgLST: dictionary of y-axis data
    Output:
    shows a 2x2 grid of density plots
    """
    # creating the 2x2 grid 
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    
    # calling density plot and assigning each plot to a spot on the grid
    im = createDensity(avgNdvi["winter"], avgLST["winter"], axs[0, 0])
    im = createDensity(avgNdvi["spring"], avgLST["spring"], axs[0, 1])
    im = createDensity(avgNdvi["summer"], avgLST["summer"], axs[1, 0])
    im = createDensity(avgNdvi["fall"], avgLST["fall"], axs[1, 1])

    # putting colorbars next to each plot
    fig.colorbar(im, ax=axs[0, 0], orientation='vertical', label = "Density")
    fig.colorbar(im, ax=axs[0, 1], orientation='vertical', label = "Density")
    fig.colorbar(im, ax=axs[1, 0], orientation='vertical', label = "Density")
    fig.colorbar(im, ax=axs[1, 1], orientation='vertical', label = "Density")

    # labeling
    axs[0,0].set_title("Winter")
    axs[0,1].set_title("Spring")
    axs[1,0].set_title("Summer")
    axs[1,1].set_title("Fall")
    
    # plotting    
    plt.tight_layout()
    plt.show()
