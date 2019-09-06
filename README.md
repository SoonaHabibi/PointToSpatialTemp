# WEST Consultants
## Umpqua

#### Input:
1. Point gage temperature timeseries for all the events (in fahrenheit); timeseriese contains missing value
2. Spatial climatalogical PRISM mean tempreture (in Celsius) with high resolution of 800 m over the USA
3. Metadata containing Latitude and Longitude of all the rain gages' station

#### Output:
1. hourly spatial timeseries of tempreture in Fahrenheit for the entire duration of all the events (.tif)

#### SubFunction:
1. BasicFunction_py3.py

#### Procedure:
1. Reading PRISM data (.bil)
2. Extract the desire PRISM temp for our study area(BoundaryBox)
3. For each event find the begining and end of the event and generate hourly timeseries
4. Read all files (each file contains observation for a specific rain gage) for the event and check if there is any temp observation at that specific hour
5. if there was any observation, the gage temp and PRISM tempreture at the gage location (Latitude and Longitude) will be add to the points data set for interpolation (X,Y)
6. Fit a linear regression at each hour and then apply the model to the entire PRISM matrix to generate the estimated tempreture and save it as a tif file
7. create and save R square timeseries to check the quality of our result

