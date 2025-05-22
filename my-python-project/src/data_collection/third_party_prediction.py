import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
load_dotenv()
import time
def get_prediction_from_third_party_api(
  latitude: float,
  longitude: float,
  timezone: str,
) -> pd.DataFrame:
  """
  Fetches weather forecast data from a third-party API.

  Args:
      latitude (float): Latitude of the location.
      longitude (float): Longitude of the location.
      start_date (str): Start date for the forecast in YYYY-MM-DD format.
      end_date (str): End date for the forecast in YYYY-MM-DD format.
      timezone (str): Timezone for the forecast.

  Returns:
      list: List of dictionaries containing weather forecast data.
  """
  API_URL = os.getenv("THIRD_PARTY_URL")
  params ={
    "latitude": latitude,
    "longitude": longitude,
  }
  
  API_KEY = os.getenv("THIRD_PARTY_API_KEY")
  headers = {
    "x-api-key": API_KEY
  }
  time.sleep(2)
  response = requests.get(API_URL, headers=headers, params=params,timeout=10)
  # Check if the request was successful
  if response.status_code == 200:
    data = response.json()
    rows = []
    # Convert the timezone string to a pytz.timezone object
    target_timezone = pytz.timezone(timezone)
    for x in range(len(data['data'])):
      if data['data'][x]['model_data']:
        quality = data['data'][x]['quality']
        blue_start = data['data'][x]['magics']['blue_hour'][0]
        blue_end = data['data'][x]['magics']['blue_hour'][1]
        golden_start = data['data'][x]['magics']['golden_hour'][0]
        golden_end = data['data'][x]['magics']['golden_hour'][1]
        #When is sunrise the blue hour comes first and when is sunset the golden hour comes first
        #API Send some none values, for now we will ignore them
        try:
          time_period_start = min(blue_start, golden_start)
          time_period_end = max(blue_end, golden_end)
        except Exception as e:
          print(f"Error processing time periods: {e}")
          continue
        #Create a dataframe with the data for the time period
        # Convert from UTC to the target timezone and remove timezone info
        time_period_start = datetime.fromisoformat(time_period_start.replace("Z", "+00:00")).astimezone(target_timezone).replace(tzinfo=None)
        time_period_end = datetime.fromisoformat(time_period_end.replace("Z", "+00:00")).astimezone(target_timezone).replace(tzinfo=None)
        # Round time_period_start down to the nearest 10-minute mark
        time_period_start = time_period_start - timedelta(
            minutes=time_period_start.minute % 10,
            seconds=time_period_start.second,
            microseconds=time_period_start.microsecond
        )
        # Generate normalized time intervals (e.g., 22:10, 22:20, etc.)
        current_time = time_period_start
    
        while current_time <= time_period_end:
          rows.append({"time": current_time.strftime("%Y-%m-%d %H:%M:%S"), "api_prediction": quality})
          current_time += timedelta(minutes=10)  # Increment by 10 minutes
    # Check if rows is empty
    if not rows:
      raise Exception('No data found on 3rd party API')
    df = pd.DataFrame(rows)
    df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None)
    return df
  else:
    print(f"Error: {response.status_code} - {response.text}")
    raise Exception(f"Error fetching data from API: {response.status_code} - {response.text}")
