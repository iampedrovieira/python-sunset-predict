import requests
import pytesseract
from PIL import Image
from io import BytesIO
import re
import numpy as np
import json
from datetime import datetime
import pandas as pd

# === Download image from URL ===
def download_image(url):
  response = requests.get(url)
  response.raise_for_status()
  return Image.open(BytesIO(response.content))

# === OCR Metadata Text ===
def extract_forecast_metadata(image):
  text = pytesseract.image_to_string(image)

  metadata = {}

  #match_init = re.search(r"Initialized:\s*(\d{2}Z\d{1,2}[A-Z]{3}\d{4})", text)
  match_hour = re.search(r"Forecast Hour:\s*\[(\d+)\]", text)
  match_valid = re.search(r"Valid at:\s*(\d{2}Z\s*[A-Z]{3}\s*\d{1,2}\s*\d{4})", text)
  
  #if match_init:
  #  metadata["initialized_str"] = match_init.group(1)

  if match_hour:
      metadata["forecast_hour"] = int(match_hour.group(1))

  if match_valid:
      z, month, day, year = re.findall(r"(\d{2}Z)\s*([A-Z]{3})\s*(\d{1,2})\s*(\d{4})", match_valid.group(1))[0]
      metadata["valid_str"] = f"{z}{int(day):02d}{month}{year}"
  return metadata

# === Parse time string ===
def parse_time(zulu_str):
  hour = int(zulu_str[:2])
  dt = datetime.strptime(zulu_str[3:], "%d%b%Y")
  return datetime(dt.year, dt.month, dt.day, hour).isoformat() + "Z"

# === Heuristic: RGB to Quality % ===
def rgb_to_quality(rgb):
  r, g, b = [v / 255.0 for v in rgb]
  return int(np.clip((r - b + 1) / 2 * 100, 0, 100))

# === OCR Lat/Lon Labels ===
def detect_latlon_bounds(image):
  text = pytesseract.image_to_string(image)
  lat_matches = re.findall(r"(\d{1,2})°[ ]?[NS]", text)
  lon_matches = re.findall(r"(\d{1,3})°[ ]?[EW]", text)

  lats = sorted({int(x) for x in lat_matches})
  lons = sorted({int(x) for x in lon_matches})

  if len(lats) >= 2 and len(lons) >= 2:
      return min(lats), max(lats), min(lons), max(lons)
  else:
      # Default fallback
      return 33, 63, -20, 40

# === Extract grid data ===
def extract_quality_data(image, lat_min, lat_max, lon_min, lon_max, step=10):
  img = image.convert("RGB")
  width, height = img.size
  data = []

  for y in range(0, height, step):
    for x in range(0, width, step):
      rgb = img.getpixel((x, y))
      lat = lat_max - (y / height) * (lat_max - lat_min)
      lon = lon_min + (x / width) * (lon_max - lon_min)
      data.append({
          "latitude": round(lat, 2),
          "longitude": round(lon, 2),
          "sunset_quality_percent": rgb_to_quality(rgb)
      })

  return data

# === Main processing function ===
def process_sunset_image_from_url(url):
  image = download_image(url)

  metadata = extract_forecast_metadata(image)
  lat_min, lat_max, lon_min, lon_max = detect_latlon_bounds(image)

  parsed = {
      #"initialized": parse_time(metadata["initialized_str"]),
      "forecast_hour": metadata["forecast_hour"],
      "valid_at": parse_time(metadata["valid_str"]),
      #"initialized_str": metadata["initialized_str"],
      "valid_str": metadata["valid_str"]
  }

  result = {
      "title": "Sunset Quality Forecast",
      "source": "sunsetwx.com",
      "model": "GFS",
      **parsed,
      "lat_range": [lat_min, lat_max],
      "lon_range": [lon_min, lon_max],
      "units": {"sunset_quality_percent": "0 to 100"},
      "data": extract_quality_data(image, lat_min, lat_max, lon_min, lon_max, step=10)
  }

  return result

# === Replace with actual URL ===
image_url = ""
json_data = process_sunset_image_from_url(image_url)

#Create a Datafram with Latitude, Longitude and sunset_quality_percent,time and a hash with all the data from each row
df = pd.DataFrame(json_data["data"])
df["time"] = json_data["valid_at"]
df["latitude"] = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)
df["sunset_quality_percent"] = df["sunset_quality_percent"].astype(float)
#The timezone is on UTC
df["time"] = pd.to_datetime(df["time"]).dt.tz_convert("UTC")
df["type"] = "sunset"
df["hash"] = df.apply(lambda x: hash((x["latitude"], x["longitude"], x["time"],x["type"])), axis=1)

print(df)

