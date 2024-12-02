import dask
import pystac_client
import planetary_computer
import leafmap
import geogif
import stackstac
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

def main(bbox, start, end):
    """
    Runs the 4 functions below and returns a plot of the mean ndwi.

    Parameters
    ----------
    bbox : tuple
        The bounding box of area of interest.
    start : list
        The beginning time point.
    end : list
        The ending time point
        
    Returns
    -------
    Returns a plot of the mean ndwi from each scene.
    
    """
    def retrieve(bbox, start, end):
        """
        Collects the imagery from planetary computer.
    
        Parameters
        ----------
        bbox : tuple
            The bounding box of area of interest.
        start : list
            The beginning time point.
        end : list
            The ending time point
            
        Returns
        -------
        Returns the images within the time points within the bounding box.
        
        """
        catalog = pystac_client.Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            modifier=planetary_computer.sign_inplace,)
        search = catalog.search(
            collections = ['landsat-c2-l2'],
            bbox = bbox,
            datetime = start[0] + "/" + end[0]
        )
        items = search.get_all_items()
        return items
    def search(items, bbox):
        """
        Clips the images to the bounding box and selects B3 and B8.
    
        Parameters
        ----------
        items : list
            The list of all bands of all images.
        bbox : tuple
            The bounding box of the area of interest.
            
        Returns
        -------
        Returns a stack of the images within the time points within the bounding box.
        
        """
        stack = stackstac.stack(items, assets=["TM_B3", "TM_B4", "TIRS_B10"], bounds_latlon=bbox)
        return stack
    def ndvi(stack):
        """
        Calculates NDWI for each image 
    
        Parameters
        ----------
        stack : dataarray
            Stack of all of the images with bands 3 and 8.
            
        Returns
        -------
        Returns a dataarray of NDWI for each image
        
        """
        B3 = stack.sel(band = "TM_B3")
        B4 = stack.sel(band = "TM_B4")
        ndvi = (B4 - B3) / (B3 + B4)
        return ndvi
    def plot(avg):
        """
        Creates a scatterplot with the NDWI for each scene with time on the x axis and NDWI on the y axis 
    
        Parameters
        ----------
        avg : dataarray
            Stack of the average NDWI for each scene
        """
        times = avg['time'].values
        plt.rcParams['figure.figsize'] = (12,8)
        plt.figure(figsize = (5, 5))
        plt.scatter(x=times, y=avg)
        plt.xlabel("Time")
        plt.ylabel("Mean NDVI")
        plt.show()

    items = retrieve(bbox, start, end)
    stack = search(items, bbox)
    avg = ndvi(stack)
    plot(ndvi)