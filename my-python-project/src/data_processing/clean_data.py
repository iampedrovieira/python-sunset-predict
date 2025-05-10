

def remove_outside_data(data):
  """
  Remove outliers from the data. Data ouside the sunset and sunrise hours.
  We are using the sola angle to determine the sunrise and sunset hours.
  6 degrees is the limit for the solar angle.
  Args:
      data (pd.DataFrame): The DataFrame containing the data to be cleaned.
  Returns:
      pd.DataFrame: The cleaned DataFrame with outliers removed.
  """
  return data[(data['apparent_elevation'] >= -7) & (data['apparent_elevation'] <= 7)]