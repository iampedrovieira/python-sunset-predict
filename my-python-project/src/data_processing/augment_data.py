
# Add a hash column with dataframe data
import pandas as pd
import hashlib
def hash_row(row):
  """
  Hash a row of the DataFrame.
  
  Args:
      row (pd.Series): The row to hash.
      
  Returns:
      str: The hash of the row.
  """
  # Convert the row to a string and encode it
  row_str = row.to_string(index=False)
  return hashlib.sha256(row_str.encode()).hexdigest()

def create_column_df(df: pd.DataFrame,column_name, value) -> pd.DataFrame:
  """
  Create a new column in the DataFrame with a constant value.
  Args:
      df (pd.DataFrame): The DataFrame to modify.
      column_name (str): The name of the new column.
      value: The value to assign to the new column.
  Returns:
      pd.DataFrame: The modified DataFrame with the new column.
  """
  # Create a new column with the specified value
  df[column_name] = value
  
  return df

def extend_df(df:pd.DataFrame)->pd.DataFrame:
  """
  Extend the DataFrame with additional columns.
  
  Args:
      df (pd.DataFrame): The DataFrame to extend.
      
  Returns:
      pd.DataFrame: The extended DataFrame.
  """
  # Create a new column with the hash of the DataFrame
  #df = create_column_df(df, "hash", df.apply(hash_row, axis=1))
  #df = create_column_df(df, "web_prediction", pd.Series([pd.NA] * len(df), dtype="Float64"))
  #df = create_column_df(df, "time_before", df["time"] - pd.Timestamp.now())
  #df = create_column_df(df, "third_party_score", pd.Series([pd.NA] * len(df), dtype="Float64"))

  return df