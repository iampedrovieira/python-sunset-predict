import pandas as pd

def merge_data_by_time(forecast_raw, air_quality_raw, solar_angle_raw,third_party,img_prediction_raw):
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
  #Classify the solar angle data
  events = []
  for i in range(len(solar_angle_df)):
    if i == 0:
      # First row, cannot determine trend
      events.append("unknown")
    else:
      prev_angle = solar_angle_df.iloc[i - 1]['apparent_elevation']
      curr_angle = solar_angle_df.iloc[i]['apparent_elevation']
      if curr_angle > prev_angle:
          events.append("sunrise")
      else:
          events.append("sunset")
  for i in range(len(events) - 1):
    if events[i] == "unknown" and events[i + 1] == "sunrise":
      events[i] = "sunrise"
    if events[i] == "unknown" and events[i + 1] == "sunset":
      events[i] = "sunset"
  solar_angle_df['type'] = events
  solar_angle_df['time'] = pd.to_datetime(solar_angle_df['time']).dt.tz_localize(None)
  

  img_prediction_sunset_df = img_prediction_raw[img_prediction_raw['type'] == 'sunset']
  img_prediction_sunset_df = img_prediction_sunset_df[['time','sunset_quality_percent']]
  # Set the 'time' column as the index
  img_prediction_sunset_df.set_index('time', inplace=True)
  img_prediction_sunset_df = img_prediction_sunset_df.resample('10min').interpolate(method='linear')
  img_prediction_sunset_df.reset_index(inplace=True)
  img_prediction_sunset_df.loc[:, 'type'] = 'sunset'
  
  img_prediction_sunrise_df = img_prediction_raw[img_prediction_raw['type'] == 'sunrise']
  img_prediction_sunrise_df = img_prediction_sunrise_df[['time','sunset_quality_percent']]
  # Set the 'time' column as the index
  img_prediction_sunrise_df.set_index('time', inplace=True)
  img_prediction_sunrise_df = img_prediction_sunrise_df.resample('10min').interpolate(method='linear')
  img_prediction_sunrise_df.reset_index(inplace=True)
  img_prediction_sunrise_df.loc[:, 'type'] = 'sunrise'
  
  img_prediction_raw = pd.concat([img_prediction_sunset_df, img_prediction_sunrise_df], ignore_index=True)

  merged_df = pd.merge(forecast_df, air_quality_df, on="time", how="inner")
  merged_df = pd.merge(merged_df, solar_angle_df, on="time", how="inner")
  merged_df = pd.merge(merged_df, third_party, on="time", how="left")
  merged_df = pd.merge(merged_df, img_prediction_raw, on=["time","type"], how="left")
  #Rename columns in the merged DataFrame
  merged_df.rename(columns={
      'sunset_quality_percent': 'img_prediction',
      'third_party_prediction': 'api_prediction'
  }, inplace=True)
  
  return merged_df

