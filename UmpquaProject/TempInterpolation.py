# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 09:11:40 2019

@author: sardekani
"""
import sys
sys.path.append("//westfolsom/Office/Python/WEST_Python_FunctionAug2019");
import BasicFunction_py3 as BF
import pandas as pd
import numpy as np
import datetime
from datetime import datetime, timedelta
import csv
from osgeo import gdal
from osgeo.gdalconst import GA_ReadOnly
import glob
from sklearn.linear_model import LinearRegression
import os
import matplotlib.pyplot as plt

PRISM_path = "//westfolsom/Office/PRISM/normals_800m/tmean/PRISM_tmean_30yr_normal_800mM2_annual_bil.bil"
dir = "//westfolsom/projects/2019/UmpquaRiver/Precipitation_Temperature/"
events_file = dir + 'event.csv'
events = pd.read_csv(events_file)
event_name = events.iloc[:,1]

dir_gage = dir + 'GageCoordinate.csv'
latlon = pd.read_csv(dir_gage)
BoundaryBox = [-124.41, -121.8, 42.625, 44.18]
###############
## reading Prism raster file
dataset = gdal.Open(PRISM_path)
band = dataset.GetRasterBand(1)
cols = dataset.RasterXSize
rows = dataset.RasterYSize
proj = dataset.GetProjection()

transform = dataset.GetGeoTransform()
xOrigin = transform[0]
yOrigin = transform[3]
pixelWidth = transform[1]
pixelHeight = -transform[5]

data = band.ReadAsArray(0, 0, cols, rows)

points_list = [tuple(latlon['Long']),tuple(latlon['Lat'])]

colAr = []
rowAr = []
tempAr = []
for i in range(len(points_list[0])):
    col = int((points_list[0][i] - xOrigin) / pixelWidth)
    colAr.append(col)
    row = int((yOrigin - points_list[1][i] ) / pixelHeight)
    rowAr.append(row)
    temp = (data[row][col])*9/5+32
    tempAr.append(temp)
    print(col, row, temp)
    
df = pd.DataFrame([colAr, rowAr, tempAr]).transpose()
df.columns = ['col', 'row', 'temp']
PrismTemp = pd.concat([latlon, df], axis=1)                       #data frame with temp (PRISM), lat, long, station name

###############
## creating points_list for each hour to do interpolation
for i in range(len(event_name)):
    DirName = event_name[i]
    path = dir + DirName +'/hourly/'
    allfiles = glob.glob(path + '*.csv')
    StartDate = datetime.strptime(events.iloc[i,3],'%Y_%m_%d')
    EndDate = datetime.strptime(events.iloc[i,2],'%Y_%m_%d') + timedelta(days=1)
    duration = (EndDate - StartDate).days*24+(EndDate - StartDate).seconds/3600
    r_sq_Ar = []
    date_Ar = []
    for j in range(int(duration)):
        gageAr = []
        prismAr = []
        matrix = np.zeros((rows,cols))
        date = StartDate+timedelta(hours=j)
        date_str = datetime.strftime(date, '%Y-%m-%d %H:%M:%S') 
        for ii in range(len(allfiles)):
            GagePath = allfiles[ii]
            gage_df = pd.read_csv(GagePath)
            ind = np.where(gage_df['date']==date_str)
            if len(ind[0])==1:
                temp_gage = gage_df['temp'].iloc[ind]
                if not np.isnan(temp_gage.item()):
                    gageAr.append(temp_gage.item()) 
                    station_name = gage_df['station'].iloc[1]
                    ind2 = np.where(PrismTemp['Gage_ID']==station_name)
                    temp_prism = PrismTemp['temp'].iloc[ind2]
                    prismAr.append(temp_prism.item())
                else: print(temp_gage)
            
        ########
        ## we have data set for the interpolation
        x = np.array(prismAr).reshape(-1,1)
        y = np.array(gageAr)
        model = LinearRegression().fit(x,y)
        r_sq = model.score(x,y)
        r_sq_Ar.append(r_sq)
        date_Ar.append(date)
        a = model.coef_
        b = model.intercept_
        matrix[data<0] = data[data<0]
        matrix[data>=0] = a*data[data>=0] + b
        Tiffile_dir = dir + 'temp_interpol/' + event_name[i] +'/'
        if not os.path.exists(Tiffile_dir): os.mkdir(Tiffile_dir)
        Tiffile = Tiffile_dir + datetime.strftime(date, '%Y%m%d_%H%M%S') + '.tif'
        BF.CreateMatrixFileFloat(Tiffile, matrix, cols, rows, transform, proj)
        
        
    r_sq_df = pd.DataFrame([date_Ar, r_sq_Ar]).transpose()
    r_sq_df.columns = ['date','R2']
    r_sq_out = dir + 'temp_interpol/r_sq/' + event_name[i] + '.csv'
    r_sq_df.to_csv(r_sq_out, index=False)












#for i in range(len(event_name)):                 # this part is for fixing the time format
#    DirName = event_name[i]
#    path = dir + DirName +'/hourly/'
#    allfiles = glob.glob(path + '*.csv')
#    for ii in range(len(allfiles)):
#        GagePath = allfiles[ii]
#        gage_df = pd.read_csv(GagePath)
#
#        if len (gage_df['date'].iloc[0])>19:
#            gage_df['date'] = gage_df['date'].apply(lambda x: x[0:19])
#            gage_df.to_csv(GagePath, index=False)
#        print (gage_df['date'].iloc[0])