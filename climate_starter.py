#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import datetime as dt


# # Reflect Tables into SQLAlchemy ORM

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#Import Flask 
from flask import Flask, jsonify

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)


# View all of the classes that automap found
Base.classes.keys()


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Set welcome page
@app.route("/")
def welcome():
    """List all available api routes."""
    
    return (
        f"<h2>Available Routes for Measurements Table in 'hawaii.sqlite' Database:</h2><br/>"

        f'<h3><a href="/api/v1.0/station">/api/v1.0/station</a></h3><br/>'
        f'<h3><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a><br/>'
        f'<a href="/api/v1.0/tobs">/api/v1.0/tobs</a><br/>'

        f"<p><h2>Routes for Measurements Dates:</h2></p>"

        f'<h3><a href="/api/v1.0/<start>">/api/v1.0/<start></a></h3><br/>'

        f"<h3>Please pic the dates between '2010-01-01' and '2017-08-23'</h3>"
        f"<h3>Supported Formats : (2010-01-01, 2010.01.01, 2010 01 01, 2010%01%01)</h3><br/><br/>"

    )

#################################################   #################################################
# Calculate start_date, End_date(most recent date) 
                                # and the date one year from the last date in data set.
#################################################   #################################################

# Create our session (link) from Python to the DB
session = Session(engine)

# Find start date
start_date_Q = session.query(Measurement).order_by(Measurement.date).first()
start_date = start_date_Q.date

# Find the most recent date in the data set.
most_recent_date = session.query(Measurement).order_by(Measurement.date.desc()).first()
date= most_recent_date.date


# Make sure to close the session
session.close()


# Calculate the date one year from the last date in data set.

# convert string to datetime object to avoid error
date_time_obj = dt.datetime.strptime(date, '%Y-%m-%d').date()
# Find timedelta between latest date and 12 months ago
date_12months_ago = date_time_obj- dt.timedelta(days=365)
#convert the datetime object back to string
date_12months_ago = date_12months_ago.strftime('%Y-%m-%d')
date_12months_ago


#################################################
# Flask Routes
#################################################

#API route for precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    """Return a list of Measurement data ie, Date, and Precipitation of each Measurement
     in the form of Dictionary """
   
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    prcp_date = session.query(Measurement.date, Measurement.prcp).all()

    # Make sure t close the session
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    measurement_date_prcp = []
    for date, prcp in prcp_date:
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

#API route for tobs
@app.route("/api/v1.0/tobs")
def tobs():
    
    """Return a JSON list of temperature observations (TOBS) for the previous year."""   
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    # List the stations and the counts in descending order.
    station_count = func.count(Measurement.station)
    most_active_st_qry = session.query(Measurement.station , station_count).\
                                       group_by(Measurement.station).\
                                       order_by(station_count.desc()).first()
    
    most_active_station = most_active_st_qry[0]
    
    # Using the most active station id,
    #Query the dates and temperature observations of the most active station for the last year of data.
    station_last_12mon_date_temp = session.query(Measurement.date, Measurement.tobs).\
                          filter(Measurement.station == most_active_station).\
                          filter(Measurement.date >= date_12months_ago).all()  
    
    # Close Session
    session.close()
    
    #Get the list of temperature observations (TOBS) for the previous year.
    station_last_12mon_temp = [item[1] for item in station_last_12mon_date_temp ]
    
    # Convert list of tuples into normal list
    active_station_tobs = list(np.ravel(station_last_12mon_temp)) 
    
    return jsonify(active_station_tobs)


# API route for start
import re

@app.route("/api/v1.0/<start>")
def measurement_by_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
        for a given start for all dates greater than and equal to the start date."""
    print(start)
    # Create our session (link) from Python to the DB
    session = Session(engine)

    clean_start_date = re.sub(r'[^0-9]+', '-', start)
    print(f"start = {start} \n clean_start: {clean_start_date}")

    measuremet_date_obj = session.query(Measurement.date).all()
    Mdatemeasuremet_date = list(np.ravel(measuremet_date_obj)) 
    
    if clean_start_date in Mdatemeasuremet_date:
        tobs_min = func.min(Measurement.tobs)
        tobs_avg = func.avg(Measurement.tobs)
        tobs_max = func.max(Measurement.tobs)

        measurement_date = session.query(tobs_min, tobs_avg, tobs_max).\
                                         filter(Measurement.date >= clean_start_date).first()
        
        # Close Session
        session.close()

        return jsonify({"tobs_min": measurement_date[0] , "tobs_avg": measurement_date[1] , "tobs_max": measurement_date[2]})

    else:
        return jsonify({"error": f"Start Date : {clean_start_date} not found!"}), 404



if __name__ == '__main__':
    app.run(debug=True)



