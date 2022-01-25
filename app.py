from flask import Flask, json, jsonify
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np


engine = create_engine("sqlite:///titanic.sqlite")

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
def home():
     return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2017-08-20<br/>"
        f"/api/v1.0/2017-08-17/2017-08-20<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():

    session = Session(engine)
    
    # Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    year_ago = dt.datetime(2017,8,23)- dt.timedelta(days = 365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago).\
    order_by(Measurement.date).all()

    dates = [result[0] for result in results]
    prcps = [result[1] for result in results]

    # Save the query results in a dictionary - keys=dates and values=prcps
    prcp_dict = dict(zip(dates, prcps))
    precip = {date: prcp for date, prcp in results}
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Station.station).all()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    year_ago = dt.datetime(2017,8,23)- dt.timedelta(days = 365)

    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    # List the stations and the counts in descending order.
    observation_counts = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    most_active_station = observation_counts[0][0]
    
    # Query the last 12 months of tobs data for this station and plot the results as a histogram
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.station == most_active_station).\
        order_by(Measurement.date).all()

    dates = [result[0] for result in results]
    temps = [result[1] for result in results]

    # Save the query results in a dictionary - keys=dates and values=temps
    prcp_dict = dict(zip(dates, temps))
    
    return jsonify(prcp_dict)

@app.route("/api/v1.0/<start>")
def start_tobs(start):
    
    session = Session(engine)

    min = session.\
        query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).first()
    max = session.\
        query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).first()
    avg = session.\
        query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).first()

    list= [min[0], max[0], avg[0]]
    return jsonify(list)

@app.route("/api/v1.0/<start>/<end>")
def start__end_tobs(start, end):
    
    session = Session(engine)

    min = session.\
        query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).first()
    max = session.\
        query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).first()
    avg = session.\
        query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).first()

    list= [min[0], max[0], avg[0]]
    return jsonify(list)




if __name__ == "__main__":
    app.run(debug=True)