#################################################
# Import dependencies
#################################################
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# Import Flask
from flask import Flask, redirect, jsonify

#################################################
# Database Setup
#################################################
# Create connection to the sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

""" * Home page.
	* List all routes that are available."""
@app.route("/")
def home():
	print("Server received request for 'Home' page.")
	return ("Welcome to the Surfs Up Weather API!<br><br>"
		f"Available Routes:<br>"
		f"Precipitation for last year: /api/v1.0/precipitation<br/>"
        f"List of all stations: /api/v1.0/Station<br/>"
        f"Date and temperature observations from the last year: /api/v1.0/tobs<br/>"        
        f"Min, Avg, Max Temp given a start date : /api/v1.0/(Y-M-D)<br/>"
        f"Min, Avg, Max Temp given a start and end date: /api/v1.0/(start=Y-M-D)/(end=Y-M-D)<br/>"
	)

""" * Convert the query results to a Dictionary using date as the key and prcp as the value.
	* Return the JSON representation of your dictionary."""
@app.route("/api/v1.0/precipitation")
def precipitation():
	# Query all Measurments
	results = session.query(Measurement).all()
	# Close the Query
	session.close()

	#Create a dictionary using 'date' as the key and 'prcp' as the value.
	year_prcp = []
	for result in results:
		year_prcp_dict = {}
		year_prcp_dict["date"] = result.date
		year_prcp_dict["prcp"] = result.prcp
		year_prcp.append(year_prcp_dict)

	# Jsonify summary
	return jsonify(year_prcp)

""" * Return a JSON list of stations from the dataset."""
@app.route("/api/v1.0/Station")
def stations():
	"""Return a list of all station names"""
	# Query all stations
	results = session.query(Station.station).all()
	# Close the Query
	session.close()

	# Convert list of tuples into normal list
	all_station = list(np.ravel(results))

	# Jsonify summary
	return jsonify(all_station)

""" * query for the dates and temperature observations from a year from the last data point.
	* Return a JSON list of Temperature Observations (tobs) for the previous year."""
@app.route("/api/v1.0/tobs")
def temperature():
	# Find last date in database then subtract one year
	Last_Year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

	# Query tempurature observations
	temperature_results = session.query(Measurement.tobs).filter(Measurement.date > Last_Year).all()
	# Close the Query
	session.close()

	# Convert list of tuples into normal list
	temperature_list = list(np.ravel(temperature_results))

	# Jsonify summary
	return jsonify(temperature_list)

""" * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
	* When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date. 
	* When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
@app.route("/api/v1.0/<start>")
def single_date(start):
	# Set up for user to enter date
	Start_Date = dt.datetime.strptime(start,"%Y-%m-%d")

	# Query Min, Max, and Avg based on date
	summary_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
	filter(Measurement.date >= Start_Date).all()
	# Close the Query
	session.close() 
	
	summary = list(np.ravel(summary_stats))

	# Jsonify summary
	return jsonify(summary)

# Same as above with the inclusion of an end date
@app.route("/api/v1.0/<start>/<end>")
def trip_dates(start,end):
	# Set up for user to enter dates 
	Start_Date = dt.datetime.strptime(start,"%Y-%m-%d")
	End_Date = dt.datetime.strptime(end,"%Y-%m-%d")

	# Query Min, Max, and Avg based on dates
	summary_stats = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
	filter(Measurement.date.between(Start_Date,End_Date)).all()
	# Close the Query
	session.close()    
	
	summary = list(np.ravel(summary_stats))

	# Jsonify summary
	return jsonify(summary)

if __name__ == "__main__":
	app.run(debug=True)