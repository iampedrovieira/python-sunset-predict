

"""
This module collects forecast data from the External API.
It retrieves:
- daily data for:
  - shortwave radiation sum (MJ/m²);
- hourly data for:
  - cloud cover (total, low, mid, high) (%);
  - visibility (meters);
  - relative humidity at 2m (%);
  - temperature at 2m (°C);
  - dew point at 2m (°C);
  - diffuse radiation (W/m²);
  - direct radiation (W/m²);
  - wind speed at 10m (km/h);
  - wind direction at 10m (°);
  - wind gusts at 10m (km/h).

The results are ready to save in a database.
"""
import requests
import os
from dotenv import load_dotenv
import time
# Load environment variables from .env file
load_dotenv()

def collect_forecast_data(lat:float, long:float, start_date:str, end_date:str, timezone:str) -> dict:
  base_url = os.getenv("FORECAST_API_URL")
  API_URL = (
    f'{base_url}'
    f"?latitude={lat}"
    f"&longitude={long}"
    f"&daily=shortwave_radiation_sum"
    "&hourly=visibility,cloud_cover_high,cloud_cover_mid,cloud_cover_low,cloud_cover,temperature_2m,relative_humidity_2m,dew_point_2m,diffuse_radiation,direct_radiation,wind_speed_10m,wind_direction_10m,wind_gusts_10m"
    f"&start_date={start_date}"
    f"&end_date={end_date}"
    f"&timezone={timezone}"
    f"&model=icon"  # Specify the DWD ICON model
   )
  for i in range(10):
    try:
      response = requests.get(API_URL,timeout=30)
      if response.status_code == 200:
        data = response.json()
        hourly_data_forecast_data = []
        # Extract daily data
        daily_data = data.get("daily", {})
        for i in range(len(daily_data)):
          processing_day = daily_data['time'][i]
          shortwave_radiation_sum = daily_data['shortwave_radiation_sum'][i]
          for j in range(len(data['hourly']['time'])):
            # Extract hourly data
            data_time = data['hourly']['time'][j]
            if data_time[:10] != processing_day:
              continue

            cloud_cover = data['hourly']['cloud_cover'][j]
            cloud_cover_low = data['hourly']['cloud_cover_low'][j]
            cloud_cover_mid = data['hourly']['cloud_cover_mid'][j]
            cloud_cover_high = data['hourly']['cloud_cover_high'][j]
            visibility = data['hourly']['visibility'][j]
            temperature_2m = data['hourly']['temperature_2m'][j]
            relative_humidity_2m = data['hourly']['relative_humidity_2m'][j]
            dew_point_2m = data['hourly']['dew_point_2m'][j]
            diffuse_radiation = data['hourly']['diffuse_radiation'][j]
            direct_radiation = data['hourly']['direct_radiation'][j]
            wind_speed_10m = data['hourly']['wind_speed_10m'][j]
            wind_direction_10m = data['hourly']['wind_direction_10m'][j]
            wind_gusts_10m = data['hourly']['wind_gusts_10m'][j]

            # Create a structured dictionary to return
            final_data = {
              "time": data_time,
              "latitude": lat,
              "longitude": long,
              "shortwave_radiation_sum": shortwave_radiation_sum,
              "cloud_cover": cloud_cover,
              "cloud_cover_low": cloud_cover_low,
              "cloud_cover_mid": cloud_cover_mid,
              "cloud_cover_high": cloud_cover_high,
              "visibility": visibility,
              "temperature_2m": temperature_2m,
              "relative_humidity_2m": relative_humidity_2m,
              "dew_point_2m": dew_point_2m,
              "diffuse_radiation": diffuse_radiation,
              "direct_radiation": direct_radiation,
              "wind_speed_10m": wind_speed_10m,
              "wind_direction_10m": wind_direction_10m,
              "wind_gusts_10m": wind_gusts_10m
            }
            # Append the data to the list
            hourly_data_forecast_data.append(final_data)
              
        return hourly_data_forecast_data
      else:
        raise Exception(f"Failed to retrieve data. Status code: {response.status_code}")      
    except Exception as e:
      print('Failed to retrieve data. Retrying...' + str(i+1)+'/10',flush=True)
      print('Delaying for 5 seconds...',flush=True)
      time.sleep(5)
      
  raise Exception(f"Failed to retrieve data. No response from API after 5 attempts.",flush=True)