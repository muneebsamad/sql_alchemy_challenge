# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    return(
        f'Welcome to Climate App<br/>'
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/&lt;start&gt; (replace &lt;start&gt; with start date in yyyy-mm-dd format)<br/>'
        f'/api/v1.0/&lt;start&gt;/&lt;end&gt; (replace &lt;start&gt; and &lt;end&gt; with start and end dates in yyyy-mm-dd format)<br/>'
    )

@app.route ("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from today
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query to retrieve the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                          filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

# Define route to retrieve stations
@app.route("/api/v1.0/stations")
def stations():
    # Query to retrieve stations
    stations = session.query(Station.station, Station.name).all()
    
    # Convert the query results to a list of dictionaries
    station_list = [{"station": station, "name": name} for station, name in stations]
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
                           group_by(Measurement.station).\
                           order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Calculate the date one year ago from today
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query to retrieve temperature observations for the most active station for the last year of data
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == most_active_station).\
                filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary
    tobs_dict = {date: tobs for date, tobs in tobs_data}
    
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Convert start date string to datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    
    # Query to retrieve temperature statistics for dates greater than or equal to the start date
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                 filter(Measurement.date >= start_date).all()
    
    # Convert the query results to a list
    temp_stats_list = list(np.ravel(temp_stats))
    
    return jsonify(temp_stats_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Convert start and end date strings to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    
    # Query to retrieve temperature statistics for dates between the start and end dates
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                 filter(Measurement.date >= start_date).\
                 filter(Measurement.date <= end_date).all()
    
    # Convert the query results to a list
    temp_stats_list = list(np.ravel(temp_stats))
    
    return jsonify(temp_stats_list)

if __name__ == '__main__':
    app.run(debug=True)
