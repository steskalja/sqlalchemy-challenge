import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
# Function to calucate date range (Last date present in the database and previous year date)
def date_calc():
    #Retreive the latest date present in the database
    Latest_date = session.query(func.max(Measurement.date)).all()
   
    #Calculating 1 year date range
    today = dt.date.today()
    #Format the latest date in date format
    Lastest_date_datefmt = today.replace(year=int(Latest_date[0][0][:4]),\
                                        month=int(Latest_date[0][0][5:7]),\
                                        day=int(Latest_date[0][0][8:]))
    
    # Calculate the date 1 year ago from the latest_date
    One_Year_backdate = Lastest_date_datefmt-dt.timedelta(days=365)
    
    This_Year_rd = Lastest_date_datefmt.strftime("%Y-%m-%d")
    Previous_Year_sd = One_Year_backdate.strftime("%Y-%m-%d")
    
    Year_list = [Previous_Year_sd,This_Year_rd]
    return(tuple(Year_list))
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
    return(
        f"Note: Paste the routes in the browsing after the default link<br/>"
        f"Available Routes Below:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/<start><br/>"
        f"Put the start date in 'YYYY-MM-DD' format<br/>"
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"   
        f"Put the dates in 'YYYY-MM-DD/YYYY-MM-DD' format<br/>"
        )  

@app.route("/api/v1.0/precipitation")
def precipitation():
    """
        Query for the dates and temperature observations from the last year.
        Convert the query results to a Dictionary using date as the key and tobs as the value.
        Return the JSON representation of your dictionary.
        
        Important Notes: Instead of tobs, performing the query for prcp as the route states "precipitation".
                        Returning list of dictionaries.
                        Also, to make it more clear, I am adding the station id.
    """
    # Calling date_calc function to get the start & end date of the previous year
    Range = date_calc()
    rd = Range[1]
    sd = Range[0]
    # Query for the dates and temperature observations from the last year.
    results = session.query(Measurement.date, Measurement.station,Measurement.prcp).\
                                       filter(Measurement.date <= rd).\
                                       filter(Measurement.date >= sd).all()                                                                  
    list = []
    for result in results:
        dict = {"Date":result[0],"Station":result[1],"Precipitation":result[2]}
        list.append(dict)
    return jsonify(list)

@app.route("/api/v1.0/stations")
def stations():
    """ Return a JSON list of stations from the dataset in the form of dictionary.
        Note: returning a JSON list of dictionaries instead of just list.
    """    
    stations = session.query(Station.station,Station.name).all()
    
    list=[]
    for station in stations:
        dict = {"Station ID:":stations[0],"Station Name":stations[1]}
        list.append(dict)

    return jsonify(list)

@app.route("/api/v1.0/tobs")
def tobs():
    """ Return a JSON list of Temperature Observations (tobs) for the previous year."""  
    Range = date_calc()
    rd = Range[1]
    sd = Range[0]
    tobs = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date <= rd).filter(Measurement.date >= sd).all()
    list = []
    for temp in tobs:
        dict = {"date": temp[0], "tobs": temp[1]}
        list.append(dict)

    return jsonify(list)  

@app.route("/api/v1.0/<start>")
def tstart(start):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).order_by(Measurement.date.desc()).all()
    #list = []
    print(f"Temperature Analysis for the dates greater than or equal to the start date")
    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
    return jsonify(dict) 

@app.route("/api/v1.0/<start>/<end>")
def tstartend(start,end):         
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.date.desc()).all()
    print(f"Temperature Analysis for the dates greater than or equal to the start date and lesser than or equal to the end date")
    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
    return jsonify(dict)   