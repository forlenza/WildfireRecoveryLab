
# Vegetation Recovery after Wildfire
## Michael Forlenza
### Analyze relationship between recovery from wildfire and terrain (slope and aspect)

### Functions written by Galen Maclaurin, updated by Ricardo Oliveira, reclassify the DEM into different zones by slope and aspect
# Files utilized:
## All files use the coordinate system EPSG:32613 - WGS 84 / UTM zone 13N, Units: meters
- bigElk_dem.tif : containing elevation values for Big Elk, Colorado ranging from 1,925 m to 3,173m
- fire_perimeter.tif: cells with a value of 1 are considered within the fire perimeter, while areas of NoData are transitional, and cells equaling 2 are outside of the perimeter
- a series of tifs in the format L5034032_2002_B4.tif, which contain bands 3 and 4 of Landsat imagery for years following the fire in Big Elk


# Functions:
- getNDVI(band3file,band4file)
    - Opens and reads the files by joining them with directory, computes and returns ndvi for the year
    for the entire extent of the tif
     - the names of files are passed as strings, earlier placed in a dictionary
    - returns the NDVI for the year specified
- getRR(year, ndvi)
    - Calculates the Recovery Ratio for each pixel within the burned areas and calculates average Recovery Ratio for the entire area
    - Returns a numpy array, which is a surface of the RR values for each pixel for that year
- getCOR()
    - Computes and returns coefficient of recovery (COR) for burned area, returning a numpy array of the coefficient of recovery for the entire area across all years
- zonalStats(zone,value,name)
    - Gets the zonal statistics of the Coefficient of Recovery surface by slope or aspect zones, and exports as a csv
- expTiff(CoR)
    - Writes a GeoTiff of the coefficient of recovery surface

# Lab Instructions:
## *Part 1*
1. Read in DEM as numpy array, calculate slope and aspect (using provided functions)
    1. reclassify aspect grid to 8 cardinal directios (N,NE,E,etc)
    2. reclassify slope grid into 10 classes using provided function
2. Calculate the Normalized Difference Vegetation Index (NDVI) for all years of analysis
3. Calculate the Recovery Ratio (RR) for each pixel for each year:
    RR = (NDVI)/mean NDVI of healthy forest
    1. mean NDVI is a different constant each year, found using Boolean indexing
4. Calculate trend of recovery ratio for each pixel
    1. use polyfit from Scipy to fit first-degree polynomial, which fits a least squares trend line
    2. polyfit() returns 2 values, slope (coefficient of recovery) and intercept (not needed)
5. Print mean RR for each year, print mean coefficient of recovery across all years for burned area

## *Part 2*
1. Write a generic function that calculates Zonal Statistics as Table
    1. use two numpy arrays (zone raster and value raster)
    2. calculate mean, standard deviation, min max, and count
    3. create a Pandas dataframe with the output, write to a csv
        - csv should have zone field and the five statistics
        - csv should have as many rows as there are unique values
2. Calculate zonal stats of coefficient of recovery for:
    - each terrain slope class
    - *and* for each cardinal direction of aspect
    1. produce two output csvs, one for slope and one for aspect
    2. exclude all pixels outside of fire perimeter using numpy.nan
3. Export final coefficient of recovery
    
