from data_collection.collect_forecast_data import collect_forecast_data
from data_collection.air_qualiy import get_air_quality_data
from data_collection.solar_angle import calculate_solar_angle
from data_collection.third_party_prediction import get_prediction_from_third_party_api
from db.db_connection import create_connection, close_connection
from data_processing.merge_data import merge_data_by_time
from data_processing.clean_data import remove_outside_data
from data_processing.augment_data import extend_df

import pandas as pd
if __name__ == "__main__":
  # Example usage
  latitude = 55.6761  # Example latitude (Copenhagen)
  longitude = 12.5683  # Example longitude (Copenhagen)
  start_date = "2025-05-12"  # Example start date
  end_date = "2025-05-14"    # Example end date
  timezone = "Europe/Copenhagen"
  
  try:
    forecast_data = collect_forecast_data(latitude, longitude, start_date, end_date, timezone)
    air_quality_data = get_air_quality_data(latitude, longitude, start_date, end_date,timezone)
    solar_angle_data = calculate_solar_angle(latitude, longitude, start_date, end_date, timezone)
    third_party_data = get_prediction_from_third_party_api(latitude, longitude, timezone)
    
    merged_df = merge_data_by_time(forecast_data, air_quality_data, solar_angle_data, third_party_data)
    data = remove_outside_data(merged_df)
    extended_df = extend_df(data)
    conn = create_connection()
    data.to_sql('weather_data', conn, if_exists="append", index=False)
    close_connection(conn)
    
  except Exception as e:
    #Save the error to the database
    conn = create_connection()
    error_df = pd.DataFrame({"error": [str(e)], "timestamp": [pd.Timestamp.now()]})
    error_df.to_sql('error_log', conn, if_exists="append", index=False)
    close_connection(conn)
  
