import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, redirect, url_for


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

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start-end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    # Query all dates & prcp values
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and append to a list of all_prcp values
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Measurement.station).distinct().all()
    
    all_stations = list(np.ravel(results))
    # Return a JSON list of stations from the dataset
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations from a year from the last data point.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > query_date).all()

    # Create a dictionary from the row data and append to a list of all_tobs values
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/start/<start>")
def start_date(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).all()

    from_start_dict = {}
    from_start_dict["Min"] = results[0][0]
    from_start_dict["Avg"] = results[0][1]
    from_start_dict["Max"] = results[0][2]

    
    return jsonify(from_start_dict)

@app.route("/api/v1.0/start-end/<start>/<end>")
def range_start_end(start, end):
    # When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    start_end_dict = {}
    start_end_dict["Min"] = results[0][0]
    start_end_dict["Avg"] = results[0][1]
    start_end_dict["Max"] = results[0][2]

    
    return jsonify(start_end_dict)  

if __name__ == '__main__':
    app.run(debug=True)