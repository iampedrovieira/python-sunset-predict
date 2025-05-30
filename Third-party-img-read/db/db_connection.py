import pandas as pd
import sqlite3
from datetime import datetime

def create_connection(db_file: str):
  """ create a database connection to a SQLite database """
  conn = None
  # Check if the database file exists
  try:
      conn = sqlite3.connect(db_file)
      print(f"Connection to {db_file} successful")
  except sqlite3.Error as e:
      print(e)
  return conn

def close_connection(conn):
  """ close the database connection """
  if conn:
      conn.close()
      print("Connection closed")
  else:
      print("No connection to close")


def save_to_db(data: pd.DataFrame, table_name: str):
  """
  Save the DataFrame to a SQLite database
  """
  conn = create_connection()
  try:
      data.to_sql(table_name, conn, if_exists='append', index=False)
      print(f"Data saved to {table_name} table")
  except sqlite3.Error as e:
      print(f"Error saving data to {table_name}: {e}")
  finally:
      close_connection(conn)