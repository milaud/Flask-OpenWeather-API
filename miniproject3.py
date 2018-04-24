from flask import Flask, render_template, request, jsonify
import json
import requests
import urllib2
#from urllib.request import urlopen
import numpy as np
import pandas as pd
import StringIO
import base64
import datetime
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

"""
Helper Methods
"""
def weather_forecast(city):
    params = { 'q'    : city, 
               'APPID': '7dac7c6773baa744b0f774fea7ee3730', 
               'units': 'imperial'
             }
    res = requests.get('http://api.openweathermap.org/data/2.5/weather', params=params)
    return res.json()

def weather_5_day_forecast(city):
    params = { 'q'    : city, 
               'APPID': '7dac7c6773baa744b0f774fea7ee3730', 
               'units': 'imperial'
             }
    res = requests.get('http://api.openweathermap.org/data/2.5/forecast', params=params)
    return res.json()
"""
HTTP Routes
"""
@app.route('/')
def main():
  return render_template('index.html')

@app.route('/', methods=['POST'])
def displayWeather():
    cityName = request.form['text']
    currentTemp = weather_forecast(cityName)
    forecast = weather_5_day_forecast(cityName)

    # Returns status code of weather JSON
    statusCode = str(currentTemp['cod'])

    if statusCode == '404':
        return page_not_found(statusCode)
    elif statusCode == '500':
        return internal_server_error(statusCode)
    elif statusCode == '200':
        # Returns the list tuple in forecast JSON
        fiveDayList = forecast['list']
        dates = []
        temps = []

        for i in fiveDayList:
            # Gets the timestamp as YYYY-MM-DD HH:MM:SS
            listDate = i['dt_txt']

            monthDay = datetime.datetime.strptime(listDate, "%Y-%m-%d %H:%M:%S").strftime("%m-%d-%Y")

            # Gets the temperature as a string
            #listTemperatureString = str(i['main']['temp'])

            # Gets temp as a float
            listTemperature = i['main']['temp']

            """
            The JSON response returns a temperature for every 3rd hour
            We change the date to this format: MM-DD-YYYY
            We check if the new date (in new format) is in our list, if it is we skip that date
            We only want 5 unique days
            """
            # Adds date into list of dates
            if monthDay in dates:
                continue
            else:
                dates.append(monthDay)
                # Adds temperatures to list of temps
                temps.append(listTemperature)

        currentConditions = currentTemp['weather'][0]['description']
        conditionsIconCode = currentTemp['weather'][0]['icon']

        # To get the image, plug conditionsIconCode into URL
        # http://openweathermap.org/img/w/{}.png
        # ex. http://openweathermap.org/img/w/10d.png

        plt.plot(dates, temps, color='blue', linestyle='solid', marker='D')
        plt.xlabel("Date")
        plt.ylabel('Temperature (' + u"\u00b0" + 'F)')
    
        img = StringIO.StringIO()
        sns.set_style("dark")
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue())

        # Close the graph so only one location forecase is 
        # plotted at a time
        plt.close()
        
        temperature = currentTemp['main']['temp']
        tempString = str(temperature) + u"\u00b0" + ' F' #u"\u00b0" is unicode for the degree symbol
        return render_template('forecast.html', city=cityName, temp=tempString, conditions=currentConditions, icon=conditionsIconCode, plot_url=plot_url)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
	
if __name__ == '__main__':
  #app.debug = True	
  app.run(port=33507)

