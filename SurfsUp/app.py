# Import the dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurements = Base.classes.measurement
Stations = Base.classes.station
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Define the most recent date and one year ago
most_recent_date = session.query(func.max(Measurements.date)).scalar()
most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
one_year_ago = most_recent_date - dt.timedelta(days=365)

# Define routes
@app.route("/")
def welcome():
    """List of routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurements.date, Measurements.prcp)\
        .filter(Measurements.date >= one_year_ago)\
        .order_by(Measurements.date)\
        .all()
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    station_results = session.query(Stations.station).all()
    stations_list = [station[0] for station in station_results]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = session.query(Measurements.station, func.count(Measurements.station))\
        .group_by(Measurements.station)\
        .order_by(func.count(Measurements.station).desc())\
        .first()[0]
    tobs_results = session.query(Measurements.date, Measurements.tobs)\
        .filter(Measurements.station == most_active_station)\
        .filter(Measurements.date >= one_year_ago)\
        .all()
    tobs_list = [{'date': date, 'tobs': tobs} for date, tobs in tobs_results]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    temp_results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs))\
        .filter(Measurements.date >= start_date)\
        .all()
    temp_list = [{'TMIN': result[0], 'TAVG': result[1], 'TMAX': result[2]} for result in temp_results]
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def calc_temps_start_end(start, end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    temp_results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs))\
        .filter(Measurements.date >= start_date)\
        .filter(Measurements.date <= end_date)\
        .all()
    temp_list = [{'TMIN': result[0], 'TAVG': result[1], 'TMAX': result[2]} for result in temp_results]
    return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)
