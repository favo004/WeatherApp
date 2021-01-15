import tkinter as tk
from tkinter import PhotoImage, ttk
from tkinter import font
from tkinter.constants import DISABLED, HORIZONTAL, NORMAL, VERTICAL
from PIL import Image, ImageTk
import os, sys
import math

from api import weather_api as Api
from utils import location as User
from utils import utils

class WeatherGui:

    def __init__(self, master):
        self.master = master
        self.user = User.UserLocation()
        self.weather_data = None
        self.current_weather = None
        self.loading_data = False

        self.hourly_images = []
        self.daily_images = []

        self.current_percipitation_image = None
        self.daily_percipitation_image = None

        self.heading_font = font.Font(family="Consolas", size=12, weight="bold")

        self.main_frame = ttk.Frame(self.master)
        self.user_interface(self.master)

        self.main_page(self.main_frame)
        self.main_frame.pack()

        self.update_weather_btn()   
        
    def user_interface(self, master):
        
        interface_frame = tk.Frame(master)

        self.update_btn = ttk.Button(interface_frame, text="Refresh", padding=(5, 5))
        self.update_btn.config(command=self.update_weather_btn)
        self.update_btn.pack()

        interface_frame.pack(anchor='ne', padx= 15, pady= 10)

    def main_page(self, master):
        
        if self.weather_data is None:
            # No weather data is available
            self.error_widget(master)
        else:
            self.current_weather_widget(master)          
            self.hourly_weather_widget(master)
            self.daily_weather_widget(master)

    def error_widget(self, master):
        self.error_frame = tk.Frame(master)
        self.error_frame.pack(padx=0, pady=200)
        self.error_frame.config(width=400, height=600)

        tk.Label(self.error_frame, font = self.heading_font, text = "There was an issue obtaining weather data.").pack()
        tk.Label(self.error_frame, font = self.heading_font, text = "Check your internet connection.").pack()

    def current_weather_widget(self, master):
        self.today_frame = tk.Frame(master, bg='blue')
        self.today_frame.pack(fill='both')
        self.today_frame.config(height=150)

        # Location frame
        self.label_frame = tk.Frame(self.today_frame)
        self.label_frame.pack(fill='both')
        self.label_frame.config(height = 30)

        ttk.Label(self.label_frame, font=self.heading_font, text="Current Weather").place(x=10, y=0)

        # Current weather frame
        self.weather_frame = tk.Frame(self.today_frame) 
        self.weather_frame.pack(fill='both')
        self.weather_frame.config(pady=10)

        self.datetime_frame = tk.Frame(self.weather_frame)
        self.datetime_frame.grid(row=0, column=0)
        self.datetime_frame.config(padx=20)

        # Location
        location = self.user.city
        ttk.Label(self.datetime_frame, font = self.heading_font, text = location).pack()

        # Date
        dt = Api.utc_to_datetime(self.weather_data['current']['dt'])
        current_date = dt.strftime("%B %d %Y")
        current_time = dt.strftime("%I:%M %p")

        self.current_date = ttk.Label(self.datetime_frame, text = current_date, anchor='w')
        self.current_date.pack()
        # self.current_time = ttk.Label(self.datetime_frame, text = current_time, anchor='w')
        # self.current_time.pack()

        # Temp
        self.temp_data_frame = tk.Frame(self.weather_frame)
        self.temp_data_frame.grid(row=0, column=1)
        self.temp_data_frame.config(padx=15)

        current_temp = str(round(self.weather_data['current']['temp'])) + chr(176)
        max_temp = "High: " + str(round(self.weather_data['daily'][0]['temp']['max'])) + chr(176)
        min_temp = "Low: " + str(round(self.weather_data['daily'][0]['temp']['min'])) + chr(176)

        ttk.Label(self.temp_data_frame, font = self.heading_font, text = current_temp).pack()
        ttk.Label(self.temp_data_frame, font = self.heading_font, text = max_temp).pack()
        ttk.Label(self.temp_data_frame, font = self.heading_font, text = min_temp).pack()

        self.weather_type_date_frame = tk.Frame(self.weather_frame)
        self.weather_type_date_frame.grid(row=0, column=2)
        self.weather_type_date_frame.config(padx=15)

        # Get Image
        key = str(self.weather_data['current']['weather'][0]['main'])
        self.current_img = self.get_weather_image(key)

        self.image_label = ttk.Label(self.weather_type_date_frame)
        self.image_label.config(image=self.current_img)
        self.image_label.pack()
        ttk.Label(self.weather_type_date_frame, font = self.heading_font, text = key).pack()

        # Percipitation
        percipitation_frame = tk.Frame(self.weather_type_date_frame, padx=20)

        if self.current_percipitation_image is None:
            self.current_percipitation_image = self.get_weather_image("percipitation",24)

        percipitation_percent = str(round(self.weather_data['daily'][0]['pop'] * 100)) + '%'

        ttk.Label(percipitation_frame, image = self.current_percipitation_image).pack(side="left")
        ttk.Label(percipitation_frame, font = self.heading_font, text = percipitation_percent).pack(side="left")

        percipitation_frame.pack()

        # Wind
        wind_speed = "Wind: " + str(round(self.weather_data['daily'][0]['wind_speed'])) + " MPH "
        wind_direction = Api.wind_deg_to_direction(self.weather_data['daily'][0]['wind_deg'])

        ttk.Label(self.weather_type_date_frame, font = self.heading_font, text = wind_speed + wind_direction).pack()

    def update_weather_btn(self):

        self.loading_data = True

        self.update_btn["state"] = DISABLED
        self.update_btn.config(text="Getting data...")
        self.update_btn.update_idletasks()

        self.main_frame.destroy()

        self.update_weather_data()

        self.main_frame = tk.Frame(self.master)
        self.main_page(self.main_frame)
        self.main_frame.pack()

        # Quick pause before enabling update button
        self.update_btn.after(1000, self.enable_update_btn)

    def enable_update_btn(self):
        self.loading_data = False

        self.update_btn.config(text="Refresh")
        self.update_btn.update()
        self.update_btn["state"] = NORMAL

    # Hourly weather data
    def hourly_weather_widget(self, master):
        self.today_hourly_frame = tk.Frame(master)

        ttk.Label(self.today_hourly_frame, font = self.heading_font, text = "Hourly Weather", padding = (10, 0)).pack(anchor='nw')

        canvas = tk.Canvas(self.today_hourly_frame, scrollregion=(0, 0, 2592, 90), bg='yellow')
        scrollbar = ttk.Scrollbar(self.today_hourly_frame, orient = HORIZONTAL, command = canvas.xview)
        scrollable_frame = ttk.Frame(canvas)

        canvas.create_window((0, 0), window = scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set, width=1200, height=100)
        
        self.hourly_images = []
        
        for index, data in enumerate(self.weather_data['hourly']):
             self.hourly_widget(scrollable_frame, data, index)    

        self.today_hourly_frame.pack()

        canvas.pack(side="top", fill="both")
        scrollbar.pack(side="bottom", fill="x")
        
    # Adds hour weather data to widget
    def hourly_widget(self, frame, data, index):
        self.hourly = tk.Frame(frame)
        self.hourly.grid(row = 0, column = index, padx=10, pady=5)

        key = data['weather'][0]['main']
        self.hourly_images.append(self.get_weather_image(key))

        self.image_frame = tk.Frame(self.hourly)
        self.image_frame.pack(fill='both')

        tk.Label(self.image_frame, image = self.hourly_images[index], width=50, height=50).pack(fill='both')

        time_of_day = Api.utc_to_datetime(data['dt']).strftime("%I:%M %p")
        ttk.Label(self.hourly, text = time_of_day).pack()

        temp = str(round(data['temp'])) + chr(176)
        ttk.Label(self.hourly, font = self.heading_font, text = temp).pack()

    # 7 day weather data
    def daily_weather_widget(self, master):

        self.daily_frame = ttk.Frame(master)

        ttk.Label(self.daily_frame, font = self.heading_font, text = "Daily Weather", padding = (10, 5)).pack(anchor='nw')

        self.daily_canvas = tk.Canvas(self.daily_frame, scrollregion=(0, 0, 370, 480), bg='yellow')
        scrollbar = ttk.Scrollbar(self.daily_frame, orient = VERTICAL, command = self.daily_canvas.yview)
        scrollable_frame = ttk.Frame(self.daily_canvas)

        self.daily_canvas.create_window((0, 0), window = scrollable_frame, anchor="nw")
        self.daily_canvas.configure(yscrollcommand=scrollbar.set, width=370, height=1200)
        self.daily_canvas.bind("<Enter>", self.bound_to_mousewheel)
        self.daily_canvas.bind("<Leave>", self.unbound_to_mousewheel)

        self.daily_images = []

        # Load in each days weather data
        for i in range(len(self.weather_data['daily'])):
            self.day_widget(scrollable_frame, i)

        self.daily_frame.pack()

        self.daily_canvas.pack(side="left", fill="both")
        scrollbar.pack(side="right", fill="y")            

    def day_widget(self, master, index):

        container_frame = tk.Frame(master)

        day_frame = tk.Frame(container_frame, padx=15, pady=10)

        # Image for weather
        key = self.weather_data['daily'][index]['weather'][0]['main']
        self.daily_images.append(self.get_weather_image(key))

        ttk.Label(day_frame, image = self.daily_images[index]).pack(side="left")

        # Date

        date = Api.utc_to_datetime(self.weather_data['daily'][index]['dt']).strftime("%B %d %Y")
        ttk.Label(day_frame, text = date, padding=(15, 0)).pack(side="left")

        # High/low temperature

        high_temp = str(round(self.weather_data['daily'][index]['temp']['max'])) + chr(176)
        low_temp = str(round(self.weather_data['daily'][index]['temp']['min']))+ chr(176)

        ttk.Label(day_frame, font = self.heading_font, text = high_temp + ' ' + low_temp, padding=(15,0)).pack(side="left")

        # Percipitation percentage

        percipitation_frame = tk.Frame(day_frame, padx=20)

        if self.daily_percipitation_image is None:
            self.daily_percipitation_image = self.get_weather_image("percipitation",24)

        percipitation_percent = str(round(self.weather_data['daily'][index]['pop'] * 100)) + '%'

        ttk.Label(percipitation_frame, image = self.daily_percipitation_image, padding=(-5, 0)).pack(side='left')
        ttk.Label(percipitation_frame, font = self.heading_font, text = percipitation_percent).pack(side="left")
        
        percipitation_frame.pack(side="left")

        day_frame.pack(fill="both")
        container_frame.pack(fill='both', side='top')

    # Gets image for weather by weather type
    def get_weather_image(self, key, size_change = 4):
        key = key.lower()
        path = utils.resource_path("assets/" + key + ".png")

        try:
            img = Image.open(path)
            size = img.size

            img = img.resize((int(size[0]/size_change), int(size[1]/size_change)), Image.ANTIALIAS)

            widget = ImageTk.PhotoImage(img)
            return widget
        except:
            # TODO: Log error Image not found
            return None
    # Updates weather data
    def update_weather_data(self):
        weather_data = Api.get_weather_by_loc(self.user, "minutely")

        self.weather_data = weather_data

    # Events for mousewheel scrolling for daily weather status
    def unbound_to_mousewheel(self, event):
        self.daily_canvas.unbind_all("<MouseWheel>")
    def bound_to_mousewheel(self, event):
        self.daily_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
    def on_mousewheel(self, event):
        self.daily_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def main():

    root = tk.Tk()
    setRootParams(root)

    app = WeatherGui(root)
    root.mainloop()

# Sets main window params
def setRootParams(root):

    # Icon
    try:
        path = utils.resource_path("assets/logo.png")
        icon = PhotoImage(file = path)
        root.iconphoto(False, icon)
    except:
        print('Error')

    # Title
    root.title("Weather App")

    # Window settings
    w = 400
    h = 600

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    x = (screen_w - w - 10)
    y = (screen_h - h - 75)

    root.geometry('%dx%d+%d+%d' % (w,h,x,y))
    root.resizable(False, False)

if __name__ == "__main__": main()