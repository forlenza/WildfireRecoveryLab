"""
Michael Forlenza
Vegetation Recovery after Wildfire
Analyze relationship between recovery and terrain (slope and aspect)
"""
import lab5functions as l5
import rasterio
import numpy as np
import pandas as pd
import os
from osgeo import gdal


# ---------------------------------Data preparation--------------------------------------------

# Directory used for most everything
DIRECTORY = "insert Dir here"
# Directory containing the bands 3 and 4
DATA_DIR = "insert directory containing infrared imagery"

# Getting the cell size of the DEM, to use in slopeAspect function:
demGdal = gdal.Open(os.path.join(DIRECTORY,"bigElk_dem.tif"),gdal.GA_ReadOnly)
pixelW = demGdal.GetGeoTransform()[1]
pixelH = demGdal.GetGeoTransform()[5]
cellSize = abs(pixelH*pixelW)
# Store dicts of the file names for each band, with the year as the key
band3Dict = {}
band4Dict = {}

yList = []
for name in os.listdir(DATA_DIR):
    year = name[9:13]
    if name.endswith("tif"):
        if name[14:16] == "B3":
            band3Dict[int(year)] = name
            yList.append(int(year))
        elif name[14:16] == "B4":
            band4Dict[int(year)] = name

print(band3Dict,band4Dict)
yearsList = sorted(yList)

FIRE_AREA = rasterio.open(os.path.join(DIRECTORY,"fire_perimeter.tif"))

with rasterio.open(os.path.join(DIRECTORY,"bigElk_dem.tif")) as dem:
    demRas = dem.read()
    # Use numpy squeeze to remove band number dimension from array
    demArray = np.squeeze(demRas,axis=0)

# Invoking aspect slope function from lab5functions
demS,demA = l5.slopeAspect(demArray, cellSize)
# Reclassify slope and aspect
demSlope = l5.reclassByHisto(demS,10)
demAspect = l5.reclassAspect(demA)


# ---------------------------------- Functions ---------------------------------


def getNDVI(band3file,band4file):
    """
    Opens and reads the files by joining them with directory, computes and returns ndvi for the year
    for the entire extent of the tif

    Parameters
    ----------
    band3file - string, the file name for band 3 (red)
    band4file - string, the file name for band4 (near infrared)

    Returns
    -------
    ndvi - numpy array,

    """
    # Pass just the strings of file name
    # Dictionary simply holds a label for the year for the NDVI
    ndviDict = {}
    year = band3file[9:13]
    with rasterio.open(os.path.join(DATA_DIR, band3file)) as b3file:
        with rasterio.open(os.path.join(DATA_DIR, band4file)) as b4file:
            b3 = b3file.read()
            b4 = b4file.read()
            #np.seterr(divide='ignore', invalid='ignore')
            ndvi = (b4.astype(float) - b3.astype(float)) / (b4 + b3)
    # Returns the array itself, and a dict with the year as a key
    ndviDict[year] = ndvi
    return ndvi

def getRR(year,ndvi):
    """
    Calculates the Recovery Ratio for each pixel, prints the average RR for the
    entire burned area for the year supplied, returns the RR as a numpy array
    Parameters
    ----------
    year - int, the year of the image, likely fetched from the yearsList
    ndvi - numpy array, returned from getNDVI

    Returns
    -------
    rr - numpy array, the recovery ratio for a given year
    """
    # Takes the year and the array created in getNDVI and finds the rate of recovery for each year
    fire = FIRE_AREA.read()
    fireArea = np.where(fire==1,1,0)
    healthyArea = np.where(fire ==2,1,0)

    # Get the areas in the NDVI that are burned and healthy
    burnedCells = fireArea * ndvi
    healthyCells = healthyArea * ndvi

    # Get the average of nonzero healthy cells' NDVI values
    avgHealthy = healthyCells[np.nonzero(healthyCells)].mean()

    # Get the recovery ratio
    rr = burnedCells / avgHealthy
    print("The average recovery ratio for ",year," is: ",rr.mean())
    return rr

def getCOR():
    """
    Computes and returns the coefficient of recovery for a burned area, to get the trend of
    the recovery ratio for each pixel across years listed above
    Returns
    -------
    newArray - numpy array, the total coefficient of recovery for the extent
    Invokes
    -------
    getNDVI(band3file,band4file)
    """
    rrList = []
    # Using getNDVI() and getRR() functions, get the RR array for each year in the list
    for year in yearsList:
        b3, b4 = band3Dict[year], band4Dict[year]
        ndvi = getNDVI(b3, b4)
        # Grab and list the RR for each year
        rr = getRR(year, ndvi)
        rr = np.squeeze(rr, axis=0)
        rrList.append(rr)
    rr = rrList[0]
    width, height = rr.shape
    newArray = np.zeros_like(rr)
    for row in range(0, width):
        for col in range(0, height):
            cellVals = []
            # Loop through each recovery ratio array, grabbing value of same pixel
            for r in rrList:
                # row, col
                val = r[row, col]
                cellVals.append(val)
            # print(cellVals)
            CoR = np.polyfit(yearsList, cellVals, 1)
            # Only first resultant value is of use
            CoR = CoR[0]
            newArray[row, col] = CoR
    avgCor = round(newArray.mean(),5)
    print("The average coefficient of recovery across all areas: ",avgCor)
    return newArray


def zonalStats(zone,value,name):
    """
    Gets the zonal statistics of the Coefficient of Recovery raster by slope or aspect,
    and exports as a csv

    Parameters
    ----------
    zone - numpy array, categorized values (slope or aspect), grouped into distinct bins
    value - numpy array, recovery ratio values for a burned area
    name - string, adds to the end of the output file name

    """
    # Get the number of distinct zones:
    zones = int(np.ptp(zone)) +1
    zoneList, meanList,sdList,minList,maxList,countList = [],[],[],[],[],[]
    # Making 1, not 0, the first zone index
    for i in range(zones)[1:]:
        # Select only the values for each zone
        zoneList.append(i)
        zoneValues = np.where(zone==i,value,0)
        #zoneValues=zoneValues[zoneValues!=0]
        # Get the statistics for that zone
        zoneMean = zoneValues.mean()
        # And append to relevant list, later to be made into dataframe
        meanList.append(zoneMean)

        zoneSd = np.std(zoneValues)
        sdList.append(zoneSd)
        zoneMin, zoneMax = np.min(zoneValues),np.max(zoneValues)
        minList.append(zoneMin)
        maxList.append(zoneMax)
        zoneCount = np.count_nonzero(zoneValues)
        countList.append(zoneCount)

    resultsDict = {
        "Zone_number":zoneList,
        "Mean":meanList,
        "Standard_deviation":sdList,
        "Min":minList,
        "Max":maxList,
        "Count":countList
    }
    df = pd.DataFrame(resultsDict)

    print(df)
    # Write to csv
    fileName = os.path.join(DIRECTORY,"OutputStatistics"+name+".csv")

    fileName = df.to_csv(fileName, index=False)


def expTiff(CoR):
    """
    Writes a geotiff of the coefficient of recovery surface

    Parameters
    ----------
    CoR - numpy array, returned by getCor
    """
    name = os.path.join(DIRECTORY,"Lab5Results.tif")
    with rasterio.open(
        name,"w",
        driver="Gtiff",
        height = CoR.shape[0],
        width = CoR.shape[1],
        count = 1,
        dtype = "float32",
        crs = FIRE_AREA.crs,
        transform = FIRE_AREA.transform,
        nodata = -99) as outRas:
        outRas.write(CoR,1)


# --------------------------------- Calling functions ---------------------------------

cor = getCOR()
expTiff(cor)

print("Statistics for Slope: ")
slopeStats = zonalStats(demSlope,cor,"Slope")

print("Statistics for Aspect: ")
aspectStats = zonalStats(demAspect,cor,"Aspect")

print("It seems like there wasn't much variance in the average coefficient of recovery for each Aspect zone, but \n"
      "zone number 3 (East) edged out the other aspects by .00009 while having the highest maximum CoR. This was\n"
      "much higher than the value for South, which I expected to have the highest average CoR as it allows for more\n"
      "sunlight. The margin is slim enough to be inconclusive. \n"
      "The slope categorized as zone 2 seemed the most plentiful and with the highest average coefficient\n"
      "of recovery .")


