from collect_forecast_data import collect_forecast_data
from airQualiy import get_air_quality_data
from solarAngle import calculate_solar_angle
import pandas as pd
if __name__ == "__main__":
  # Example usage
  latitude = 55.6761  # Example latitude (Copenhagen)
  longitude = 12.5683  # Example longitude (Copenhagen)
  start_date = "2025-05-07"  # Example start date
  end_date = "2025-05-08"    # Example end date
  timezone = "Europe/Copenhagen"
  try:
    forecast_data = collect_forecast_data(latitude, longitude, start_date, end_date, timezone)
    #Prepare the forecast data
    forecast_df = pd.DataFrame(forecast_data)
    # Convert 'time' column to datetime
    forecast_df['time'] = pd.to_datetime(forecast_df['time'])
    forecast_df.set_index('time', inplace=True)
    #This interpolates the data to 10-minute intervals
    forecast_df = forecast_df.resample('10min').interpolate(method='linear')
   
    air_quality_data = get_air_quality_data(latitude, longitude, start_date, end_date,timezone)
    #Prepare the air quality data
    air_quality_df = pd.DataFrame(air_quality_data)
    air_quality_df['time'] = pd.to_datetime(air_quality_df['time'])
    air_quality_df.set_index('time', inplace=True)
    #This interpolates the data to 10-minute intervals
    air_quality_df = air_quality_df.resample('10min').interpolate(method='linear')
    print(air_quality_df)

    solar_angle = calculate_solar_angle(latitude, longitude, start_date, end_date, timezone)
    #Prepare the sola angle data
    solar_angle_df = pd.DataFrame(solar_angle)
    solar_angle_df.reset_index(inplace=True)
    solar_angle_df.rename(columns={"index": "time"}, inplace=True)
    solar_angle_df['time'] = pd.to_datetime(solar_angle_df['time']).dt.tz_localize(None)
    
    # Merge the three DataFrames on the 'time' column
    merged_df = pd.merge(forecast_df, air_quality_df, on="time", how="inner")
    merged_df = pd.merge(merged_df, solar_angle_df, on="time", how="inner")
    
    print(merged_df)
    
  except Exception as e:
    #save on db logs
    print(f"An error occurred: {e}")
  
