# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# import ee (Main GEE API for Python)
import ee
# import gee (Default gee library is not compatible with Colab. Therefore need to load 'geemap.folium')
import geemap as gee
# import other necessary libraries
import pandas as pd
import json as json
import os as os
import eemont
import geemap.colormaps as cm
from pprint import pprint
import geopandas
import geetools as gtl
ee.Initialize()

os.chdir('/home/pc4dl/SYM2')

we_shp = 'OriginalData_WE/Boundary/WeserEms_DE_VG25KRS_WGS84.shp'
we_gpd = geopandas.read_file(we_shp)
nuts = we_gpd['NUTS'].to_list()

we_ee = gee.shp_to_ee(we_shp)
we_bbox = ee.Geometry.Rectangle(6.6392551276276492, 52.0355100156980583, 8.7114239185355977, 53.7947706785112700)

we_ee_01 = we_ee.filter("NUTS == nuts[0]")


#st_date = ('2016-03-01')
#en_date = ('2016-04-01')

TCC = {
    'bands': ['SR_B3', 'SR_B2', 'SR_B1'],
    'min': 0.0,
    'max': 0.3,
}

FCC = {
    'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
    'min': 0.0,
    'max': 0.6,
}

ndviPalette = ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718',
               '74A901', '66A000', '529400', '3E8601', '207401', '056201',
               '004C00', '023B01', '012E01', '011D01', '011301']


# Define Year
year = [*range(2010, 2020, 1)]
year = [1999]

# Define month
month = [*range(3, 10, 2)]

for yr in year:
    print("Data collection on: " + str(yr))
    
    for mo in month:
        print("Data collection on: " + str(yr) + "-" + str(mo))
        
        # Set Start and End date
        st_date = ee.Date.fromYMD(yr, mo, 1)
        en_date = st_date.advance(2, 'month')
        
        ## Landsat 5

        # L5-01 Get Landsat 5 surface reflectance collection for region of interest and years.
        L5_org = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2') \
            .filterBounds(we_ee) \
            .filterDate(st_date,en_date) \
            .filterMetadata('CLOUD_COVER', 'less_than', 60)
            
        L5_masked = (L5_org)\
            .maskClouds()\
            .scale()\
            .spectralIndices(["NDVI", "EVI", "OSAVI", "NDMI"])

        L5_selected = L5_masked.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'NDVI', 'EVI', 'OSAVI', 'NDMI'])

        L5_count = L5_selected.size()
        print('Count L5: ', str(L5_count.getInfo())+'\n')
        
        ## Landsat 7

        # L7-01 Get Landsat 8 surface reflectance collection for region of interest and years.
        L7_org = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2') \
            .filterBounds(we_ee) \
            .filterDate(st_date,en_date) \
            .filterMetadata('CLOUD_COVER', 'less_than', 60)

        L7_masked = (L7_org)\
            .maskClouds()\
            .scale()\
            .spectralIndices(["NDVI", "EVI", "OSAVI", "NDMI"])

        L7_selected = L7_masked.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'NDVI', 'EVI', 'OSAVI', 'NDMI'])

        L7_count = L7_selected.size()
        print('Count L7: ', str(L7_count.getInfo())+'\n')
        
        ## Landsat 8

        # L8-01 Get Landsat 8 surface reflectance collection for region of interest and years.
        L8_org = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
            .filterBounds(we_ee) \
            .filterDate(st_date,en_date) \
            .filterMetadata('CLOUD_COVER', 'less_than', 60)

        L8_masked = (L8_org)\
            .maskClouds()\
            .scale()\
            .spectralIndices(["NDVI", "EVI", "OSAVI", "NDMI"])

        L8_selected = L8_masked.select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'NDVI', 'EVI', 'OSAVI', 'NDMI'], 
                                       ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'NDVI', 'EVI', 'OSAVI', 'NDMI'])


        L8_count = L8_selected.size()
        print('Count L8: ', str(L8_count.getInfo())+'\n')
        
        
        ## L5, L7, & L8

        # L578-01 Merge L5, L7, and L8
        L578_selected = ee.ImageCollection(L5_selected.merge(L7_selected.merge(L8_selected)))
        L578_count = L578_selected.size()
        print('Count L578: ', str(L578_count.getInfo())+'\n')

        # L578-02 Median and clip
        L578_median_composite = L578_selected.median().clip(we_ee)
        
        
        ## Export to Drive
        desc = 'Landsat_578_' + str(yr) + '_' + str(mo)
        gee.ee_export_image_to_drive(L578_median_composite, 
                                     description = desc, 
                                     folder = 'SYM2', 
                                     region = we_bbox, 
                                     scale = 30, 
                                     file_format='GeoTIFF')

# iacs_xx = 'OriginalData_NH/IACS_NH/GJSON/we_2006.geojson'
        













"""

L578_median_composite_few = L578_median_composite.select(['EVI'])


Map = gee.Map(center=[51.3127, 9.4797], zoom=8)
Map.addLayer(we_ee, {'color': 'blue', 'fillColor': '00000000'}, 'NordHessen')
Map.addLayer(L578_median_composite, TCC, "Landsat-578")
Map.addLayer(L578_median_composite['NDVI'],{"min":0,"max":1,"palette":cm.palettes.ndvi},"NDVI")
Map.addLayer(L578_median_composite['NDMI'],{"min":0,"max":1,"palette":cm.palettes.ndvi},"NDMI")
Map

out_dir = 'L578/NH/'
filename = os.path.join(out_dir, 'NH_' + str(yr) + '_' + str(mo) + '_landsat.tif')
print(filename)

gee.ee_export_image(
    L578_median_composite_few, filename=filename, scale=30, region=we_ee.geometry(), file_per_band=False
)

we_2010 = 'OriginalData_NH/Schlagdaten_NordHesse/clip_2010.shp'
we_2010_ee = gee.shp_to_ee(we_2010)


# Add reducer output to the Features in the collection.
we_2010_mean = L578_median_composite.reduceRegions(**{
  'collection': we_2010_ee,
  'reducer': ee.Reducer.mean(),
  'scale': 30,
})

# Print the first feature, to illustrate the result.
pprint(ee.Feature(we_2010_mean.first()).select(L578_median_composite.bandNames()).getInfo())


we_2010_mean_json = gee.ee_to_geojson(we_2010_mean)
"""