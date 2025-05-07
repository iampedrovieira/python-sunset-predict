import pvlib
import pandas as pd

def calculate_solar_angle(latitude: float, longitude: float, start_date: str, end_date: str, timezone: str):
  """Use pvlib to get accurate solar elevation angle"""
  #time_zone = pytz.timezone(TIMEZONE)
  times = pd.date_range(
  start=start_date,  # Choose your time or range
  end=end_date,
  freq='10min',  # 10-minute intervals
  tz=timezone,
  )
  
  # Create location object
  location = pvlib.location.Location(latitude, longitude, tz=timezone)
  solar_position = location.get_solarposition(times)
  return solar_position[['apparent_elevation', 'azimuth']]
  