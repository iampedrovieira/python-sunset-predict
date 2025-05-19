import requests
import pytesseract
from PIL import Image

import re
import numpy as np

from datetime import datetime
import pandas as pd

def extract_forecast_metadata(image):
  text = pytesseract.image_to_string(image)
  metadata = {}
  match_hour = re.search(r"Forecast Hour:\s*\[(\d+)\]", text)
  match_valid = re.search(r"Valid at:\s*(\d{2}Z\s*[A-Z]{3}\s*\d{1,2}\s*\d{4})", text)
  if match_hour:
    metadata["forecast_hour"] = int(match_hour.group(1))

  if match_valid:
    z, month, day, year = re.findall(r"(\d{2}Z)\s*([A-Z]{3})\s*(\d{1,2})\s*(\d{4})", match_valid.group(1))[0]
    metadata["valid_str"] = f"{z}{int(day):02d}{month}{year}"
  return metadata

def detect_map_bounds(image):
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
  
# === Heuristic: RGB to Quality % ===
def rgb_to_quality(rgb):
  r, g, b = [v / 255.0 for v in rgb]
  return int(np.clip((r - b + 1) / 2 * 100, 0, 100))

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