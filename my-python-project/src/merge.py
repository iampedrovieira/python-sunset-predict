import sqlite3
import pandas as pd
import glob
import os

all_data = []
data_files = glob.glob('./data/data-*.db')
if not data_files:
  print("No data files to process.")
  #exit()
for file_name in data_files:
  print(f"Processing: {file_name}")
  conn = sqlite3.connect(file_name)
  data = pd.read_sql_query("SELECT * FROM weather_data where api_prediction is not null and img_prediction is not null", conn)
  #Create new column to know the time between the prediction and the moment
  retriever_time = pd.to_datetime(f'{file_name[12:-12]} {file_name[23:-3].replace("-", ":")}')

  # Compare only date (day, month, year)
  data['prediction_day'] = data['time'].apply(
      lambda x: 'today' if pd.to_datetime(x).date() == retriever_time.date() 
      else 'tomorrow' if pd.to_datetime(x).date() == (retriever_time + pd.Timedelta(days=1)).date()
      else 'other'
  )
  all_data.append(data)
  conn.close()
  #Move file to processed folder
  processed_folder = './data/processed'
  if not os.path.exists(processed_folder):
      os.makedirs(processed_folder)
  os.rename(file_name, os.path.join(processed_folder, os.path.basename(file_name))) 
# Combine all data
combined_data = pd.concat(all_data, ignore_index=True)
#Save combined data

conn = sqlite3.connect('./data/merged/final.db')
# Check if table exists and get existing data
try:
  existing_data = pd.read_sql_query("SELECT * FROM weather_data", conn)
  # Concatenate and remove duplicates
  all_combined = pd.concat([existing_data, combined_data], ignore_index=True)
  final_data = all_combined.drop_duplicates()
  final_data.to_sql('weather_data', conn, if_exists="replace", index=False)
except:
  # Table doesn't exist, create it
  combined_data.to_sql('weather_data', conn, if_exists="replace", index=False)
#Delete all error files
error_files = glob.glob('./data/error_*.db')
for error_file in error_files:
  os.remove(error_file)
conn.close()