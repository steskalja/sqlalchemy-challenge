import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


Base = automap_base()
Base.prepare(engine, reflect=True)


Measurement = Base.classes.measurement
Station = Base.classes.station


session = Session(engine)

def date_calc():
   
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
        f"Accessible Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/<start><br/>"
        f"'YYYY-MM-DD' format<br/>"
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"   
        f"'YYYY-MM-DD/YYYY-MM-DD' format<br/>"
        )  

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    Range = date_calc()
    rd = Range[1]
    sd = Range[0]
    
    results = session.query(Measurement.date, Measurement.station,Measurement.prcp).filter(Measurement.date <= rd).filter(Measurement.date >= sd).all()                                                                  
    list = []
    for result in results:
        dict = {"Date":result[0],"Station":result[1],"Precipitation":result[2]}
        list.append(dict)
    return jsonify(list)

@app.route("/api/v1.0/stations")
def stations():
    
    stations = session.query(Station.station,Station.name).all()
    
    list=[]
    for station in stations:
        dict = {"Station ID:":stations[0],"Station Name":stations[1]}
        list.append(dict)

    return jsonify(list)

@app.route("/api/v1.0/tobs")
def tobs():
    
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
    print(f"Temp analysis for the dates greater than or equal to the start date")
    for temps in results:
        dict = {"Min":results[0][0],"Avg":results[0][1],"Max":results[0][2]}
    return jsonify(dict) 

@app.route("/api/v1.0/<start>/<end>")
def tstartend(start,end):         
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.date.desc()).all()
    print(f"Temp analysis for the dates greater than or equal to the start date and lesser than or equal to the end date")
    for temps in results:
        dict = {"Min":results[0][0],"Avg":results[0][1],"Max":results[0][2]}
    return jsonify(dict)   