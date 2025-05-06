
import requests
from datetime import datetime, timedelta

import math

def get_clouds_forecast_DWD(lat:float, long:float, start_date:str, end_date:str, timezone:str) -> dict:
    
  api_url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={lat}"
    f"&longitude={long}"
    f"&start_date={start_date}"
    f"&end_date={end_date}"
    "&hourly=cloud_cover,cloud_cover_low,cloud_cover_high,visibility,cloud_cover_mid"
    f"&timezone={timezone}"
    "&model=icon"  # Specify the DWD ICON model
)
  # Make the API request
  response = requests.get(api_url)
  if response.status_code == 200:
    data = response.json()
    hourly_data = data.get("hourly", {})
    times = hourly_data.get("time", [])
    cloud_cover = hourly_data.get("cloud_cover", [])
    cloud_cover_low = hourly_data.get("cloud_cover_low", [])
    cloud_cover_mid = hourly_data.get("cloud_cover_mid", [])
    cloud_cover_high = hourly_data.get("cloud_cover_high", [])
    visibility = hourly_data.get("visibility", [])
    ##Create a structured dictionary to return
    could_cover_data = []

    for i in range(len(times)):
        lower_density = estimate_layer_density(cloud_cover_low[i], cloud_cover[i], visibility[i])
        mid_density = estimate_layer_density(cloud_cover_mid[i], cloud_cover[i], visibility[i])
        high_density = estimate_layer_density(cloud_cover_high[i], cloud_cover[i], visibility[i])
       
        #Create a structured dictionary to return
        forecast_data = {
            "time": times[i],
            "total_cloud_cover": cloud_cover[i],
            "low_level_cloud_cover": cloud_cover_low[i],
            "low_cloud_density_factor": lower_density,
            "mid_level_cloud_cover": cloud_cover_mid[i],
            "mid_cloud_density_factor": mid_density,
            "high_level_cloud_cover": cloud_cover_high[i],
            "high_cloud_density_factor": high_density,
            "visibility": visibility[i]
        }
        could_cover_data.append(forecast_data)
    return could_cover_data
        # Return the forecast data as a dictionary
        
def estimate_layer_density(layer_cover: float, total_cover: float, visibility: float) -> float:
    if total_cover == 0:
        return 0.0  # No clouds at all

    # Normalize values
    layer_ratio = layer_cover / 100.0
    total_ratio = total_cover / 100.0

    # Contribution of this layer to the total cloudiness
    relative_contribution = layer_ratio/ (total_ratio + 1e-6)  # Avoid division by zero

    # Sigmoid formula to calculate visibility factor
    # Set x0 to 7500 meters (where the transition happens), and k to 0.001 (steepness of the curve)
    x0 = 7500  # meters
    k = 0.002  # steepness factor

    # Calculate the visibility factor using the sigmoid function
    visibility_factor = 1 / (1 + math.exp(-k * (visibility - x0)))

    # Visibility adjustment: low visibility => more density
    visibility_factor = max(0.0, min(1.0, 1 - (visibility / 10000)))  # 10km+ is clear

    # Combine factors
    density = relative_contribution * layer_ratio + visibility_factor

    # Clip between 0 and 1
    return density

cloud_info = get_clouds_forecast_DWD(55.6761, 12.5683, "2025-05-06", "2025-05-06", "Europe/Copenhagen")
print(cloud_info)

