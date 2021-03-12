#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().run_line_magic('matplotlib', 'inline')
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt


# In[2]:


import numpy as np
import pandas as pd
import datetime as dt


# # Reflect Tables into SQLAlchemy ORM

# In[3]:


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#Import Flask 
from flask import Flask, jsonify



# In[4]:


# create engine to hawaii.sqlite
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")


# In[5]:


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# In[6]:


# View all of the classes that automap found
Base.classes.keys()


# In[7]:


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f'<a href="/api/v1.0/station">/api/v1.0/station</a><br/>'
        f'<a href="/api/v1.0/Date">/api/v1.0/Date</a><br/>'
        f'<a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a><br/>'
        f'<a href="/api/v1.0/tobs">/api/v1.0/tobs</a><br/>'
    )

# Create our session (link) from Python to the DB
session = Session(engine)

# Find the most recent date in the data set.
most_recent_date = session.query(Measurement).order_by(Measurement.date.desc()).first()

# Make sure to close the session
session.close()

print(f"Most Recent Date : {most_recent_date.date}")

# Calculate the date one year from the last date in data set.
date_12months_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
date_12months_ago



@app.route("/api/v1.0/precipitation")
def precipitation():
    
    """Return a list of Measurement data ie, Date, and Precipitation of each Measurement"""
   
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    last_12months_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_12months_ago).all()

    # Make sure t close the session
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    measurement_date_prcp = []
    for date, prcp in last_12months_data:
        prcp_dict = {}
        prcp_dict[f'{date}'] = prcp
        measurement_date_prcp.append(prcp_dict)

    return jsonify(measurement_date_prcp)

#API route for station
@app.route("/api/v1.0/station")
def station():
    
    """Return a JSON list of stations from the dataset."""   
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Design a query to calculate the total number of stations in the dataset
    stations_list = session.query(Station.station).all()

    # Make sure t close the session
    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations_list))    

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    
    """Return a JSON list of temperature observations (TOBS) for the previous year."""   
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    # List the stations and the counts in descending order.
    station_count = func.count(Measurement.station)
    most_active_st_qry = session.query(Measurement.station , station_count).\
                                       group_by(Measurement.station).order_by(station_count.desc()).first()
    
    most_active_station = most_active_st_qry[0]
    print(f"Most active station : {most_active_station}")

    # Using the most active station id,
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    station_last_12mon_temp = session.query(Measurement.tobs).\
                          filter(Measurement.station == most_active_station).\
                          filter(Measurement.date >= date_12months_ago).all()  
    
    # Close Session
    session.close()

    # Convert list of tuples into normal list
    active_station_tobs = list(np.ravel(station_last_12mon_temp)) 
    
    return jsonify(active_station_tobs)




if __name__ == '__main__':
    app.run(debug=True)



