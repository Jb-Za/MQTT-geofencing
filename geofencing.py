import pandas as pd
import numpy as np
import geopandas as gpd
import plotly_express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import matplotlib.patches as patches
import sqlite3
import shapely
import warnings



from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning) 




connection = sqlite3.connect('geofencing.db') 
df = pd.read_sql_query("SELECT * FROM geofencing", connection) # get all the location data from sqlite
connection.close() 
print (df)
gdf = gpd.GeoDataFrame( df, geometry=gpd.points_from_xy(df.longitude, df.latitude)) # creating a dataframe from the locations

px.set_ma9pbox_access_token("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$") # my api key to generate the map... i suggest getting a new one
px.scatter_mapbox(gdf, lat="latitude", lon="longitude" ,size_max=6, zoom=1, width=1200, height=800) # generates the map


polygon = gpd.read_file("geofence.geojson") # pulls the geofence from the geojson file
#print(polygon)
fig, ax = plt.subplots(figsize=(10,10)) #creating a plot of the locations
#print(gdf)
gdf.plot(ax=ax, color='black')
#print(polygon)
polygon.plot(ax=ax) #plotting the polygon
#plt.tight_layout()
#plt.axis(‘off’)
#plt.show()

#df = pd.DataFrame(location_columns, columns = ['longitude', 'latitude'])

#fig.show()

mask = (polygon.loc[0, 'geometry'])

pip_mask_geofence = gdf.within(mask) 


gdf.loc[:,'geofence'] = pip_mask_geofence # if locations are within the polygon...
gdf.sample(5)

gdf['geofence'] = gdf['geofence'].replace({True: 'In', False: 'Out'})

fig = px.scatter_mapbox(gdf, lat="latitude", lon="longitude", color="geofence" ,size_max=6, zoom=12, width=1200, height=800, mapbox_style="outdoors") # the map with all of the plots

fig.update_layout( # adding the polygon on top of it for visual clarity
    mapbox = {
        'style': "outdoors",
        'center': { 'lon': 18.000000, 'lat': -33.000000},  # i set this polygon around my house. For obvious reasons i have obscured the numbers now
        'zoom': 12, 'layers': [{
            'source': {
                'type': "FeatureCollection",
                'features': [{
                    'type': "Feature",
                    'geometry': {
                        'type': "MultiPolygon",
                        'coordinates': [[[
                            [18.000000, -33.000000],
                            [18.000000, -33.000000],
                            [18.000000, -33.000000],
                            [18.000000, -33.000000],
                            [18.000000, -33.000000]
                        ]]]
                    }
                }]
            },
            'type': "fill", 'below': "traces", 'color': "royalblue", 'opacity': 0.4}]},
    margin = {'l':0, 'r':0, 'b':0, 't':0})


fig.show() # draw the map in a browser window


