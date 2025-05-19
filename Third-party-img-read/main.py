from PIL import Image
from io import BytesIO
from datetime import datetime
import pandas as pd

from data_collection.download_images import extract_img_urls,download_img
from data_processing.process_img_into_text import extract_forecast_metadata, detect_map_bounds, rgb_to_quality
from data_processing.process_img_into_text import extract_quality_data
from db.db_connection import create_connection, close_connection
from dotenv import load_dotenv
load_dotenv()
import os

if __name__ == "__main__":
  
  #Load the environment variables
  
  THIRD_PARTY_SITE = os.getenv("THIRD_PARTY_SITE")  
  IMG_SRC_PATH_SUNSET = os.getenv("IMG_SRC_PATH_SUNSET")
  IMG_SRC_PATH_SUNRISE = os.getenv("IMG_SRC_PATH_SUNRISE")
  
  full_extraction_df = pd.DataFrame()
  base_img_src_url = [THIRD_PARTY_SITE+ IMG_SRC_PATH_SUNSET, THIRD_PARTY_SITE + IMG_SRC_PATH_SUNRISE]
  for url in base_img_src_url:
    if url == base_img_src_url[0]:
      extraction_type = "sunset"
    else:
      extraction_type = "sunrise"
    img_src_urls = extract_img_urls(url)
    print(f"Found {len(img_src_urls)} images for {extraction_type} extraction.", flush=True)
    for img_src in img_src_urls:
      print(f"Processing img...",flush=True)
      image = download_img(img_src)
      metadata = extract_forecast_metadata(image)
      lat_min, lat_max, lon_min, lon_max = detect_map_bounds(image)
      hour = int(metadata["valid_str"][:2])
      dt = datetime.strptime(metadata["valid_str"][3:], "%d%b%Y") 
      parsed_time = datetime(dt.year, dt.month, dt.day, hour).isoformat() + "Z"
      parsed = {
          "forecast_hour": metadata["forecast_hour"],
          "valid_at": parsed_time,
          "valid_str": metadata["valid_str"]
      }
      result = {
        **parsed,
        "lat_range": [lat_min, lat_max],
        "lon_range": [lon_min, lon_max],
        "data": extract_quality_data(image, lat_min, lat_max, lon_min, lon_max, step=10)
      }
      
      #Create a Datafram with Latitude, Longitude and sunset_quality_percent,time and a hash with all the data from each row
      df = pd.DataFrame(result["data"])
      df["time"] = result["valid_at"]
      df["latitude"] = df["latitude"].astype(float)
      df["longitude"] = df["longitude"].astype(float)
      df["sunset_quality_percent"] = df["sunset_quality_percent"].astype(float)
      df["type"] = extraction_type
      #The timezone is on UTC
      df["time"] = pd.to_datetime(df["time"]).dt.tz_convert("UTC")
      
      full_extraction_df = pd.concat([full_extraction_df, df], ignore_index=True)
      
  #Save dataframe on SQLITE DB
  conn = create_connection(f'./3PARTYTEST.db')
  full_extraction_df.to_sql('prediction', conn, if_exists="append", index=False)
  close_connection(conn)
  
