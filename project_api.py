import pandas as pd #importing pandas
import flask#importing flask
from flask import jsonify#importing jsonify
from flask import request
app=flask.Flask(__name__)

data=pd.read_csv("CO2 Emissions_Canada.csv")#importing the dataset.
col=data.columns#importing the colums from the dataset
df = pd.DataFrame(data, columns=col)#assigning the dataframe and colums to the value df as a datframe.
@app.route("/")#setting route for home page.
def homepage():#defining the function for homepage.
    return "<h1>Welcome</h1>"
@app.route('/api/v1/resources/data',methods=["GET"])#route to anothe page which is having the whole data.
def get_data():
    return jsonify(data.to_dict(orient='records'))#jsonified the dataframe and displaying the jasonified data.
@app.errorhandler(404)#created a error handler route to handle the errors.
def pagenot():
    return "<h1>errors occured</h1>",404
    
@app.route("/api/v1/resource/data/co2",methods=["GET"])#created a path to filter the dataset.
def filter_data():#created a function to filter the data.
    
    make = request.args.get('make', type=str)#get the make parameter fromthe url filter query
    model = request.args.get('model', type=str)#get the model parameter from the url filter query
    vehicle_class = request.args.get('vehicle_class', type=str)#get the vehicle class parameter from the url filter query
    min_engine_size = request.args.get('min_engine_size', type=float)#get the min engine size parameter from the yrl query
    max_engine_size = request.args.get('max_engine_size', type=float)#get the max engine size parameter from the url filter query
    engine_size = request.args.get('engine_size', type=float)#get the specific engine size parameter from the filter query
    min_fuel_city = request.args.get('min_fuel_city', type=float)#getting the min fuel in city parameter from url query
    max_fuel_city = request.args.get('max_fuel_city', type=float)#getting max fuel in city parameter from the url query.
    fuel_city = request.args.get('fuel_city', type=float)#getting specific value of fuel city from url query.
    min_fuel_hwy = request.args.get('min_fuel_hwy', type=float)#getting min value of fuel highway from url
    max_fuel_hwy = request.args.get('max_fuel_hwy', type=float)#getting max value of fuel highway from url.
    fuel_hwy = request.args.get('fuel_hwy', type=float)#getting specific value of fuel highway url
    min_co2_emissions = request.args.get('min_co2_emissions', type=float)#getting min co2 emission value
    max_co2_emissions = request.args.get('max_co2_emissions', type=float)#getting maimum emission value.
    co2_emissions = request.args.get('co2_emissions', type=float)#getting specific co2 emission value
    
   
    filtered_dataset= df
    if make:
        filtered_dataset = filtered_dataset[filtered_dataset['Make'].str.contains(make, case=False)]#filtering the make according to condition url
    if model:
        filtered_dataset = filtered_dataset[filtered_dataset['Model'].str.contains(model, case=False)]#filtering the model according to url
    if vehicle_class:
        filtered_dataset = filtered_dataset[filtered_dataset['Vehicle Class'].str.contains(vehicle_class, case=False)]#filtering according to vehicle class
    
    if min_engine_size:
        filtered_dataset = filtered_dataset[filtered_dataset['Engine Size(L)'] >= min_engine_size]#filtering on  engine size
    if max_engine_size:
        filtered_dataset= filtered_dataset[filtered_dataset['Engine Size(L)'] <= max_engine_size]#filtering on min enginesize
    if engine_size:
        filtered_dataset= filtered_dataset[filtered_dataset['Engine Size(L)'] == engine_size]#filtering on specific engine size
    
    if min_fuel_city:
        filtered_dataset = filtered_dataset[filtered_dataset['Fuel Consumption City (L/100 km)'] >= min_fuel_city]#filtering on min fuel city
    if max_fuel_city:
        filtered_dataset = filtered_dataset[filtered_dataset['Fuel Consumption City (L/100 km)'] <= max_fuel_city]#filtering on max fuel city
    if fuel_city:
        filtered_dataset = filtered_dataset[filtered_dataset['Fuel Consumption City (L/100 km)'] == fuel_city]#filtering on specific fuel city
    
    if min_fuel_hwy:
        filtered_dataset = filtered_dataset[filtered_dataset['Fuel Consumption Hwy (L/100 km)'] >= min_fuel_hwy]#filtering on min fuel highway
    if max_fuel_hwy:
        filtered_dataset = filtered_dataset[filtered_dataset['Fuel Consumption Hwy (L/100 km)'] <= max_fuel_hwy]#filtering on max fuel highway
    if fuel_hwy:
        filtered_dataset = filtered_dataset[filtered_dataset['Fuel Consumption Hwy (L/100 km)'] == fuel_hwy]#filtering on specific fuel highway
    if min_co2_emissions:
        filtered_dataset = filtered_dataset[filtered_dataset['CO2 Emissions(g/km)'] >= min_co2_emissions]#filtering on min co2 emission.
    if max_co2_emissions:
        filtered_dataset = filtered_dataset[filtered_dataset['CO2 Emissions(g/km)'] <= max_co2_emissions]#filtering on max co2 emission
    if co2_emissions:
        filtered_dataset = filtered_dataset[filtered_dataset['CO2 Emissions(g/km)'] == co2_emissions]#filtering on specific co2 emission
    

    result = filtered_dataset.to_dict(orient='records')#dtoring the filtered data into result
    
   
    return jsonify(result)#returning the results after jsonifying it

if __name__ == '__main__':
    app.run(debug=True)
