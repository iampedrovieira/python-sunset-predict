import traceback
from data_collection.collect_forecast_data import collect_forecast_data
from data_collection.air_qualiy import get_air_quality_data
from data_collection.solar_angle import calculate_solar_angle
from data_collection.third_party_prediction import get_prediction_from_third_party_api
from db.db_connection import create_connection, close_connection
from data_processing.merge_data import merge_data_by_time
from data_processing.clean_data import remove_outside_data
from data_processing.augment_data import extend_df
import sqlite3
import pandas as pd
from datetime import datetime
import sys

import pandas as pd
if __name__ == "__main__":
  error_file_name = "error_"+str(datetime.now().strftime("%Y-%m-%d_%H-%M"))+".db"
  full_data = pd.DataFrame()
  #Connect to the SQLite database
  conn = sqlite3.connect('./data/europe_locations.db')
  # Read the 'locations' table into a DataFrame
  locations_df = pd.read_sql('SELECT * FROM locations where population > 0 limit 5', conn)
  # Close the connection
  conn.close()
  for index,row in locations_df.iterrows():
   
    print('Process: '+row['name'],flush=True)
    latitude = float(row['latitude'])
    longitude = float(row['longitude'])
    timezone = row['timezone']
    start_date = pd.Timestamp.now().strftime('%Y-%m-%d')
    end_date = (pd.Timestamp.now() + pd.Timedelta(days=2)).strftime('%Y-%m-%d')
    #timezone = "Europe/Copenhagen"
    try:
      forecast_data = collect_forecast_data(latitude, longitude, start_date, end_date, timezone)
      air_quality_data = get_air_quality_data(latitude, longitude, start_date, end_date,timezone)
      solar_angle_data = calculate_solar_angle(latitude, longitude, start_date, end_date, timezone)
      #third_party_data = get_prediction_from_third_party_api(latitude, longitude, timezone)
      #Create a "mock" third party data
      third_party_data = pd.DataFrame({"time": pd.date_range(start=start_date, end=end_date, freq='10min'), "third_party_prediction": [0]*len(pd.date_range(start=start_date, end=end_date, freq='10min'))})
      merged_df = merge_data_by_time(forecast_data, air_quality_data, solar_angle_data, third_party_data)                        
      data = remove_outside_data(merged_df)
      #extended_df = extend_df(data)
      full_data = pd.concat([full_data, data], ignore_index=True)
      if index == 3:
        raise Exception("Test error save file on pipeline")
    except Exception as e:
      #traceback.print_exc()
      #Save the error to the database
      print('error: ' + str(e),flush=True)
      conn = create_connection(f'./data/'+error_file_name)
      error_df = pd.DataFrame({"error": [str(e)], "timestamp": [pd.Timestamp.now()]})
      error_df.to_sql('error_log', conn, if_exists="append", index=False)
      close_connection(conn)
      if '"status":400' in str(e):
        print(f"Bad Request (400) error detected for location {row['name']}. Skipping this location.")
        break
  
  error_number = 2 #Success
  if full_data.empty:
    print("No data collected.")
    error_number = 1 #Error
    sys.exit(error_number)
  if len(full_data) < 5000:
    print("Data is too small.")
    error_number = 0#Warning
  conn = create_connection(f'./data/data-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.db')
  full_data.to_sql('weather_data', conn, if_exists="append", index=False)
  close_connection(conn)
  sys.exit(error_number)
