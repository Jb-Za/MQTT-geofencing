import paho.mqtt.client as mqtt
import time
import json

import pandas as pd
import geopandas as gpd
import plotly_express as px
import matplotlib.pyplot as plt
import re
import sqlite3

from shapely.geometry import Point, Polygon

#3759233
################ if db does not exist create it ################
try:
    connection = sqlite3.connect('geofencing.db')
    sqlite_create_table_query = '''CREATE TABLE geofencing (
                                longitude FLOAT NOT NULL,
                                latitude FLOAT NOT NULL );'''

    cursor = connection.cursor()
    print("Successfully Connected to SQLite")
    cursor.execute(sqlite_create_table_query)
    connection.commit()
    print("SQLite table created")

    cursor.close()

except sqlite3.Error as error:
    print(error)
finally:
    if connection:
        connection.close()
################ if db does not exist create it ################

def insertIntoTable(longitude, latitude):
    # write to db start
        try:  
            connection    = sqlite3.connect('geofencing.db')
            cursor              = connection.cursor()
            sqlite_insert_query = """INSERT INTO geofencing
                                (longitude, latitude) 
                                VALUES 
                                (?, ?)"""

            data_t = (longitude, latitude)
            count = cursor.execute(sqlite_insert_query, data_t)
            connection.commit()
            cursor.close()

        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table:", error)
        finally:
            if connection:
                connection.close()
        # write to db end


boundaries = [(18.000000, -33.000000),
              (18.000000, -33.000000),
              (18.000000, -33.000000),
              (18.000000, -33.000000),
              (18.000000, -33.000000)]

poly = Polygon(boundaries) # create a polygon out of my properties boundaries

def on_message(client, userdata, message): 
    compiled = str(message.payload.decode("utf-8"))
    print(compiled)
    temp = re.sub(' ' ,'\t  \t' ,compiled)
    splits = re.sub(',' ,'\t  \t' ,temp) 
    result = splits.split('\t') #convoluted string splitting.. could have been better...
    #splits = [x.strip() for x in compiled.split(',')]
    #print(splits)
    latitude = result[2]
    longitude = result[8]
    insertIntoTable(longitude, latitude)

    point = Point(float(longitude), float(latitude)) 
    
    print("is within the geofence:", point.within(poly)) 




mqttBroker = "test.mosquitto.org" #
client = mqtt.Client("server")
client.connect(mqttBroker)

client.loop_start()
client.subscribe("test/flutter_location")
client.on_message = on_message
time.sleep(3000)
client.loop_stop()