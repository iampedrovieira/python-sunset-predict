import pandas as pd

def merge_data_by_time(forecast_raw, air_quality_raw, solar_angle_raw,third_party):
  """
  Merge the forecast, air quality, and solar angle data by time.

  Args:
      forecast_raw : Raw forecast data
      air_quality_raw : Raw air quality data
      solar_angle_raw : Raw solar angle data
      third_party : DF third party data
  Returns:
      pd.DataFrame: The merged DataFrame.
  """
  #Prepare the forecast data
  forecast_df = pd.DataFrame(forecast_raw)
  # Convert 'time' column to datetime
  forecast_df['time'] = pd.to_datetime(forecast_df['time'])
  forecast_df.set_index('time', inplace=True)
  #This interpolates the data to 10-minute intervals
  forecast_df = forecast_df.resample('10min').interpolate(method='linear')

  #Prepare the air quality data
  #Prepare the air quality data
  air_quality_df = pd.DataFrame(air_quality_raw)
  air_quality_df['time'] = pd.to_datetime(air_quality_df['time'])
  air_quality_df.set_index('time', inplace=True)
  #This interpolates the data to 10-minute intervals
  air_quality_df = air_quality_df.resample('10min').interpolate(method='linear')

  #Prepare the sola angle data
  solar_angle_df = pd.DataFrame(solar_angle_raw)
  solar_angle_df.reset_index(inplace=True)
  solar_angle_df.rename(columns={"index": "time"}, inplace=True)
  solar_angle_df['time'] = pd.to_datetime(solar_angle_df['time']).dt.tz_localize(None)

  merged_df = pd.merge(forecast_df, air_quality_df, on="time", how="inner")
  merged_df = pd.merge(merged_df, solar_angle_df, on="time", how="inner")
  merged_df = pd.merge(merged_df, third_party, on="time", how="left")
  #Prepare the third party data

  return merged_df

