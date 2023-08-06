# Import the dependencies.
import numpy as np
import datetime as dt


#Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func 

#Import Flask
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################

#ceate engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    """List all available API routes."""
    return (
        f"Welcome to SurfsUp API <br/>"
        f"Available Routes:<br/>"
        f"_________________________<br/>"
        f"Preceiptaion data for last 12 motnhs (2016-08-24 to 2017-08-23):<br/>"
        f"/api/v1.0/precipitation:<br/>"
        f"_________________________<br/>"
        f"List of stations in the dataset:<br/>"
        f"/api/v1.0/stations<br/>"
        f"_________________________<br/>"
        f"Date an temperature observation of the most active station (USC00519281) for previous year:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"_________________________<br/>"
        f"Minimum, Maximum and average temperature from a given start date to end of dataset:<br/>"
        f" Please enter Start Date in the format: YYYY-MM-DD<br/>"
        f"/api/v1.0/<start><br/>"
        f"_________________________<br/>"
        f"Minimum, Maximum, and average temperature from a given start date to a given end date:<br/>"
        f"Please enter Start Date and End Date in the formate: YYYY-MM-DD/YYY-MM-DD<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"_________________________"
    )
        

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Retrieve last 12 months of data"""
    
    ##create our session link from Python to the DB
    session = Session(engine)
    
    # Convert the query results from your precipitation analysis 
    # (i.e. retrieve only the last 12 months of data) to a dictionary 
    # using date as the key and prcp as the value.
    
    #find the most recent date in the dataset
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    
    #calculate the date one year ago from the last date in date set
    year_ago_date = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    #perform a query to retrieve the data and precipitaion scores
    prcp_scores = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= year_ago_date).\
                order_by(Measurement.date).all()
    
    #close session
    session.close()
    
    # Create a dictionary using date as the key and prcp as the values
    precipitation_dict = {}
    for date, prcp in prcp_scores:
        precipitation_dict[date]= prcp
        
        
    #return the JSON representation of the dictionary
    return jsonify(precipitation_dict)

   
@app.route("/api/v1.0/stations") 
def stations():

    #""" Get a list of stations"""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
        
    #perform a query to retrieve the station data
    station_data = session.query(Station.station).all()
    
    #close session
    session.close()
    
    #convert list of tuples into normal list
    station_list = list(np.ravel(station_data))
    
    #return json list of station from datatset
    return jsonify(station_list)
        
    
@app.route("/api/v1.0/tobs")
def tobs():
    """Get temperature data for the most active station for the last year"""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Find the most recent date in the dataset
    latest_date =  session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    
    #calculate the date one year from the last date in dataset
    year_ago_date = dt.datetime.strptime(latest_date,'%Y-%m-%d') - dt.timedelta(days=365)
                                            
    #find the most active station ID
    most_active_station = session.query(Measurement.station).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).first()
    
    most_active_station = most_active_station[0]
    
    
    # Perform a query to get the dates and temperature observations of the most-active station
    # for the previous year of data
    station_temp_data = session.query(Measurement.date, Measurement.tobs).\
                                filter(Measurement.station == most_active_station).\
                                filter(Measurement.date >= year_ago_date).\
                                order_by(Measurement.date).all()
                                             
    #close the session
    session.close()
                                             
   #create a list of dictionary containing dates and temperatures observations
    station_temp_list = []
    
    for date, temp in station_temp_data:
        station_temp_dict = {}
        station_temp_dict["date"] = date
        station_temp_dict["temp"] = temp
        station_temp_list.append(station_temp_dict)
                                             
    # return a JSON list of temperature data of previous year for the most active station (USC00519281)
    return jsonify(station_temp_list)
                                             
                                             
@app.route("/api/v1.0/<start>")
def start(start):
    """Get min, max, and average temperature data from start date"""
                                             
     #create our session link from pytjon to the DB
    session = Session(engine)
                                             
    #create List for date and termperature values
    sel = [Measurement.date,
           func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)]
    #perform a query to get TMIN, TAVG, and TMAX for all the dates
    # greater than or equal to the start date, taken as a parameter from the URL
    start_data = session.query(*sel).\
                filter(func.strftime('%Y-%m-%d', Measurement.date) >= start).\
                group_by(Measurement.date).\
                order_by(Measurement.date).all()
    
    #close the session
    session.close

     # Create a list of dictionary to store date, min, max and avg temperature values
    start_data_list = []
    for date, min, max, avg in start_data:
        start_dict = {}
        start_dict["date"] = date
        start_dict["min_temp"] = min
        start_dict["max_temp"] = max
        start_dict["avg_temp"] = avg
        start_data_list.append(start_dict)

    # Return a JSON list of the minimum temperature, the average temperature, and the
    # maximum temperature calculated from the given start date to the end of the dataset
        return jsonify(start_data_list)
    
@app.route("/api/v1.0/<start>/<end>")
def future(start , end):
        """ Get min, max, and average temperature data from start date to end date"""

        # Create our session link from Python to the DB
        session = Session(engine)

        # Create list for date and temperature values
        sel = [Measurement.date,
               func.min(Measurement.tobs),
               func.max(Measurement.tobs),
               func.avg(Measurement.tobs)]
        
    #Perform query to get TMIN, TAVG, and TMAX for all the dates from start date to
    # end date inclusive, taken from the URL
        start_end_data = session.query(*sel).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()
    

    #close session
        session.close

    # Create a list of dictionary to store date, min, max and avg temperature values
        start_end_data_list = []
        for date, min, max, avg in start_end_data:
                    start_dict = {}
                    start_dict["date"] = date
                    start_dict["min_temp"] = min
                    start_dict["max_temp"] = max
                    start_dict["avg_temp"] = avg
                    start_end_data_list.append(start_dict)

   # Return a JSON list of the minimum temperature, the average temperature, and the
   # maximum temperature calculated from the given start date to the given end date
        return jsonify(start_end_data_list)


#################################################

if __name__ == '__main__':
    app.run(debug=True)

     
                    

    

                                    
    