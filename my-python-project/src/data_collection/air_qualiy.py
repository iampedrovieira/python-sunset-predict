import requests

"""
This module collects air quality data from the Open-Meteo API.
It retrieves hourly data for:
  - PM10 (μg/m³);
  - PM2.5 (μg/m³);
  - aerosol optical depth (unitless);
  - nitrogen dioxide (μg/m³);
  - ozone (μg/m³);
  - European AQI (unitless index).

The results are ready to save in a database.
"""

def get_air_quality_data(latitude: float, longitude: float, start_date: str, end_date: str, timezone: str) -> dict: 
  
  api_url = (
    f"https://air-quality-api.open-meteo.com/v1/air-quality"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    f"&start_date={start_date}"
    f"&end_date={end_date}"
    f"&timezone={timezone}"
    "&hourly=pm10,pm2_5,aerosol_optical_depth,european_aqi,nitrogen_dioxide,ozone"
    )
  
  response = requests.get(api_url)
  data = response.json()
  hourly_air_quality_data = []
  if response.status_code == 200:
    data = response.json()
    for i in range(len(data['hourly']['time'])):
      # Extract hourly data
      time = data['hourly']['time'][i]
      pm10 = data['hourly']['pm10'][i]
      pm25 = data['hourly']['pm2_5'][i]
      aerosols = data['hourly']['aerosol_optical_depth'][i]
      nitrogen_dioxide = data['hourly']['nitrogen_dioxide'][i]
      ozone = data['hourly']['ozone'][i]
      
      # Create a structured dictionary to return
      air_quality_data = {
        "time": time,
        "pm10": pm10,
        "pm2_5": pm25,
        "aerosol_optical_depth": aerosols,
        "nitrogen_dioxide": nitrogen_dioxide,
        "ozone": ozone
      }
      hourly_air_quality_data.append(air_quality_data)
    return hourly_air_quality_data
  else:
    raise Exception(f"Failed to retrieve data. Status code: {response.status_code}")