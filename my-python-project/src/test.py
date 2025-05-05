import requests
from datetime import datetime, timedelta
import pytz
import math
from astral import LocationInfo
from astral.sun import sun, azimuth
import pvlib
from pvlib.location import Location

# Constants
API_KEY_OWM = ''  # Replace with your OpenWeatherMap API key
LAT = 55.676098
LON = 12.568337
TIMEZONE = 'Europe/Copenhagen'
CITY_NAME = 'Copenhagen'
REGION = 'Europe'

# Functions
def fetch_weather_data():
    """Fetch weather data from Open-Meteo API"""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}&hourly=cloudcover,relative_humidity_2m,visibility"
        f"&current_weather=true&timezone=auto"
    )
    response = requests.get(url)
    return response.json()

def fetch_pollution_data():
    """Fetch air pollution data from OpenWeatherMap"""
    url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution?"
        f"lat={LAT}&lon={LON}&appid={API_KEY_OWM}"
    )
    response = requests.get(url)
    return response.json()

def get_solar_angle_pvlib(dt: datetime):
    """Use pvlib to get accurate solar elevation angle"""
    time_zone = pytz.timezone(TIMEZONE)
    loc = Location(latitude=LAT, longitude=LON, tz=time_zone)
    solpos = loc.get_solarposition(times=[dt])
    # solar_elevation is what you're looking for
    return solpos.iloc[0]['elevation']

def get_solar_angle(dt: datetime):
    """Calculate the solar elevation angle"""
    city = LocationInfo(CITY_NAME, REGION, TIMEZONE, LAT, LON)
    s = sun(city.observer, date=dt, tzinfo=city.timezone)
    delta = dt - s['noon']
    seconds_from_noon = delta.total_seconds()
    angle = 90 - (abs(seconds_from_noon) / 240)
    return max(angle, 0)

def get_sunset_azimuth(dt: datetime):
    """Get the sun's azimuth angle at a specific datetime"""
    city = LocationInfo(CITY_NAME, REGION, TIMEZONE, LAT, LON)
    return azimuth(city.observer, dt)

def azimuth_to_direction(azimuth_deg):
    """Convert azimuth degrees to compass direction"""
    directions = ['North', 'North-East', 'East', 'South-East', 'South', 'South-West', 'West', 'North-West']
    idx = int((azimuth_deg + 22.5) / 45) % 8
    return directions[idx]

def estimate_color_metrics(cloud_cover, humidity, visibility, pm25, solar_angle):
  """
  Estimate sunset color and beauty metrics
  Returns: dict with color breakdown, intensity, beauty probability, and sun visibility %
  """
  # Color classification
  if solar_angle > 20:
      color = "Blue"
      color_score = 0
  elif 10 < solar_angle <= 20:
      color = "Yellow"
      color_score = 1
  elif 5 < solar_angle <= 10:
      color = "Orange"
      color_score = 2
  elif 2 < solar_angle <= 5:
      color = "Pink"
      color_score = 3
  else:
      color = "Purple"
      color_score = 4

  # Color percentages (only dominant color for now)
  color_percentages = {
      "Blue": 100 if color == "Blue" else 0,
      "Yellow": 100 if color == "Yellow" else 0,
      "Orange": 100 if color == "Orange" else 0,
      "Pink": 100 if color == "Pink" else 0,
      "Purple": 100 if color == "Purple" else 0,
  }

  # Color intensity based on clouds and aerosol clarity
  cloud_factor = max(0, 100 - cloud_cover) / 100
  pm25_factor = min(pm25 / 50, 1)
  intensity = int((cloud_factor + (1 - pm25_factor)) / 2 * 100)

  # Beauty prediction: only valid when sun is near horizon
  if solar_angle > 10:
      beauty_probability = 0
  else:
      color_score_weighted = color_score / 4  # 0–1
      intensity_score = intensity / 100
      cloud_score = max(0, min(1, (100 - cloud_cover) / 100))
      beauty = (color_score_weighted * 0.4 + intensity_score * 0.4 + cloud_score * 0.2)
      beauty_probability = int(min(1.0, beauty) * 100)

  # Sun visibility chance (%)
  sun_visibility = int(max(0, min(100, ((100 - cloud_cover) + (visibility / 100)) / 2)))

  return {
      "color": color,
      "color_score": color_score,
      "color_percentages": color_percentages,
      "intensity": intensity,
      "beauty_probability": beauty_probability,
      "sun_visibility": sun_visibility
  }


# Main script
def main():
    print("Fetching data...")
    tz = pytz.timezone(TIMEZONE)
    weather = fetch_weather_data()
    pollution = fetch_pollution_data()
    print(pollution)
    pm25 = pollution['list'][0]['components']['pm2_5']

    hourly = weather['hourly']
    
    for i, time in enumerate(hourly['time']):

      
       
      naive_dt = datetime.fromisoformat(time)
      
      time_date = tz.localize(naive_dt)

      solar_angle = get_solar_angle_pvlib(time_date)
      az = get_sunset_azimuth(time_date)
      direction = azimuth_to_direction(az)
      cloud_cover = hourly['cloudcover'][i]
      humidity = hourly['relative_humidity_2m'][i]
      visibility = hourly['visibility'][i]

      color_data = estimate_color_metrics(cloud_cover, humidity, visibility, pm25, solar_angle)

      print("\n======== NEW HOUR ==========")
      print(f"Time: {time_date.strftime('%Y-%m-%d %H:%M:%S')}")
      #print(f"Solar angle: {solar_angle:.2f}°")
      print(f"Sunset direction: {az:.1f}° azimuth ({direction})")
      #print(f"Cloud cover: {cloud_cover}%")
      #print(f"Humidity: {humidity}%")
      print(f"Visibility: {visibility / 1000:.1f} km")
      #print(f"PM2.5: {pm25:.2f} µg/m³")
      print(f"Predicted sky color: {color_data['color']}")
      print(f"Color intensity: {color_data['intensity']}%")
      #print(f"Color score: {color_data['color_score']} (0 = Blue, 4 = Purple)")
      print(f"Sunset beauty probability: {color_data['beauty_probability']}%")
      print(f"Sun visibility: {color_data['sun_visibility']}")
      print("============================")
      if i == 48:
        break

if __name__ == "__main__":
    main()
