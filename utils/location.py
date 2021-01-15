import requests
import json
import os
from pathlib import Path

class UserLocation:

    ip_url = 'http://ipinfo.io/json'

    def __init__(self):
        self.city = None
        self.state = None
        self.lat = None
        self.lon = None
        
        # Initialize location
        self.set_location()

    # Sets user location from local data if exists
    # If it doesn't exist we try to pull data from IP info
    def set_location(self):

        data = self.get_location_locally()

        # If no local data exists we attempt to get location via IP
        if self.lat is None or self.long is None:
            location = self.get_location()
            
            coord = location['loc'].split(',')
            self.lat = coord[0]
            self.lon = coord[1]

            self.city = location['city']
            self.state = location['region']

            self.update_local_data()

    # Returns location data from local source
    def get_location_locally(self):
        
        # Check for user data
        # If it doesn't exist we will create the file
        path = os.path.abspath("data")
        if os.path.exists(path) is False:
            os.mkdir(path)
            self.update_local_data()
        
        try:
            path = os.path.abspath("data/user.dat")
            with open(path, 'r') as file:
                data = json.load(file)

            if data is not None:
                if data['City'] is not None:
                    self.city = data['City']
                if data['State'] is not None:
                    self.state = data['State']
        except Exception as e:
            # File not found
            print('user.dat file not found', e)

    # Update user data to local source
    def update_local_data(self):

        try:
            data = {
                'City': self.city,
                'State': self.state,
                'Lat': self.lat,
                'Lon': self.lon
            }

            path = os.path.abspath("data/user.dat")
            with open(path, 'w+') as file:
                json.dump(data, file)

        except Exception as e:
            # TODO: Log error
            print('oops', e)

    # Returns latitude and longitude of user from IP info
    # Returns None if response fails
    def get_location(self):
        url = 'http://ipinfo.io/json'

        try:
            response = requests.get(url)
            data = json.loads(response.text)
        except:
            # TODO: Log response error

            return None

        if data is not None:
            return data
        else:
            return None
        