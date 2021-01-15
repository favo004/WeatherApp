import requests
import json
import math
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

last_call = None

def get_creds():
    # Get api creds from environment variable

    try:
         
        data = {
            "WEATHER_API": os.environ.get('WEATHER_API')
        }

        return data  

    except Exception as e:
        # TODO: Log Error
        print(e)
        return None
    
# Gets weather data by location obtained from users IP
def get_weather_by_loc(user, excludes):
    
    # Check if we have waited five minutes after calling the API
    if check_last_call() is False:
        return None

    # Check if user doesn't exist or user does not have longitute or latitude data stored
    if user is None or user.lon is None or user.lat is None:
        return None

    data = get_creds()

    if data is not None:

        api_key = data['WEATHER_API']
        units = "imperial"

        url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&exclude=%s&appid=%s&units=%s" % (user.lat, user.lon, excludes, api_key, units) 

        try:
            response = requests.get(url)
            data = json.loads(response.text)
            return data
        except:
            # TODO: Log error
            return None
        
    else:
        return None

# Gets current weather data by location
def get_current_weather(user):
    # Check if we have waited five minutes after calling the API
    if check_last_call() is False:
        return None

    # Check if user doesn't exist or user does not have longitute or latitude data stored
    if user is None or user.lon is None or user.lat is None:
        return None

    data = get_creds()

    if data is not None:

        api_key = data['WEATHER_API']
        units = "imperial"

        url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=%s" % (user.lat, user.lon, api_key, units) 

        try:
            response = requests.get(url)
            data = json.loads(response.text)
            return data
        except:
            # TODO: Log error
            return None
        
    else:
        return None

# Checks to see if API was called recently, if it was we won't bother calling the update as weather data is unlikely to change
# Returns True if we have not called on the API in the last 5 minutes otherwise returns False
def check_last_call():
    global last_call
    if last_call is None:
        last_call = time.time()
        return True

    # Check if 1 minute passed since last time we called on the API
    current_time = time.time()
    if current_time - last_call > 1:
        last_call = current_time
        return True
    else:
        return False

# Returns datetime of UTC timestamp
def utc_to_datetime(utc):

    dt = datetime.fromtimestamp(utc)
    return dt

# Returns direction of wind from wind degree 
def wind_deg_to_direction(degrees):

    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW" ]

    i = degrees % 360
    i = math.floor(i/45)

    return directions[i]