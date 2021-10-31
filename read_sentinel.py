# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import geemap
import ee
#import geopandas as gpd
ee.Initialize()


def degrade(time_steps, vector):
    newvector = []
    for i in range(0, len(vector)-1):
        if i % time_steps == 0:
            newvector.append(vector[i])
    return newvector

#creating datetime range

import pandas as pd
from datetime import datetime
start_date = "2018-09-09"
end_date = "2018-11-09"
date_vec = list(pd.date_range(start=start_date,end=end_date))
date_vec = degrade(6,date_vec)

for i in range(0,len(date_vec)):
    date_vec[i] = str(date_vec[i].strftime("%Y-%m-%d"))
    
    lonmin, lonmax = -2.778055556, -2.818055556
latmin, latmax = 55.00138889, 55.02138889

point = ee.Geometry.Point([lonmin, latmin]) 
polygon = [[lonmin, latmin],[lonmin, latmax],[lonmax, latmax], [lonmax, latmin]]


#retrieving the data from geempas
AscImg = []
DescImg = []
polygon1 = ee.Geometry.Polygon(polygon)
#Map.addLayer(polygon1)
points_list = []

for j in range(0, len(date_vec)-1):
    
    S1 = (ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(point)
    .filterDate(date_vec[j],date_vec[j+1])
    .select('VV'))

    for i in range(len(S1.getInfo().get('features'))):
    
        imgVV = ee.ImageCollection('COPERNICUS/S1_GRD').filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')).filter(ee.Filter.eq('instrumentMode', 'IW')).filterBounds(point).select('VV')
        desc = imgVV.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
        asc = imgVV.filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))

        descChange = (ee.Image.cat(
                desc.filter(ee.Filter.date(date_vec[j],date_vec[j+1])).mean()))

        ascChange = (ee.Image.cat(
                desc.filter(ee.Filter.date(date_vec[j],date_vec[j+1])).mean()))
    
        AscImg.append(ascChange)
        DescImg.append(descChange)
         

        data = geemap.ee_to_numpy(ee_object = descChange, region = polygon1)
        points_list.append(data)


#editing array to match format
newpoints_list = degrade(4, points_list)
for i in range(0, len(newpoints_list)):
    newpoints_list[i] = newpoints_list[i].reshape(-1)
newpoints_array = np.concatenate(newpoints_list)
#print(newpoints_array)

#creating dataframe and csv file
date_array_df = date_vec[1:]
data = {'date': date_array_df, 'Depth': newpoints_array}  
df_data = pd.DataFrame(data)

#creating filename
filename='sentinel_1@'+ str(datetime.now().strftime("%Y-%m-%d"))+'.csv'
df_data.to_csv(filename)


#string to datetime function imported from MODIS data workbook
def to_datetime_depth(dt, dp):
    datetimevec= []
    depthvec = []
    for i in range (0,len(dt)):
        if isinstance(dt[i], str) == True:
            datetime_object = datetime.strptime(dt[i],'%Y-%m-%d')
            datetimevec.append(datetime_object)
            depthpoint = dp[i]
            depthvec.append(depthpoint)
    return datetimevec, depthvec

#for the albedo data
def to_date(dt):
    datetimevec= []
    for i in range (0,len(dt)):
        if isinstance(dt[i], str) == True:
            datetime_object = datetime.strptime(dt[i],'%m/%d/%y')
            str_time = datetime.strftime(datetime_object, '%d/%m/%Y' )
            datetimevec.append(datetime_object)
    return datetimevec

#for the ndvi data
def to_date_ndvi(dt):
    datetimevec= []
    for i in range (0,len(dt)):
        if isinstance(dt[i], str) == True:
            datetime_object = datetime.strptime(dt[i],'%Y-%m-%d')
            str_time = datetime.strftime(datetime_object, '%d/%m/%Y' )
            datetimevec.append(datetime_object)
    return datetimevec

#importing data from csv file
df = pd.read_csv('/Users/sarahcliff/Desktop/Data files for project/sentinel_1@2021-10-31.csv')

date_array_list_sentinel1= list(df['date'])
depth_array = df['Depth']
date_s1, depth_s1 = to_datetime_depth(date_array_list_sentinel1, depth_array)

plt.plot(date_s1,depth_s1)
plt.xlabel('date')
plt.ylabel('depth')