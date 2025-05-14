import sqlite3
import pandas as pd
import requests
from timezonefinder import TimezoneFinder
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === 1. Configuration ===
GEOKEY_USER = os.getenv("GEOKEY_USER") 

EUROPE_CODES = {
    'AL','AD','AM','AT','AZ','BY','BE','BA','BG','HR','CY','CZ','DK',
    'EE','FI','FR','GE','DE','GR','HU','IS','IE','IT','KZ','XK','LV',
    'LI','LT','LU','MK','MT','MD','MC','ME','NL','NO','PL','PT','RO',
    'SM','RS','SK','SI','ES','SE','CH','TR','UA','GB','VA'
}

# === 2. Fetch from GeoNames ===
def fetch_geo(feature_codes, max_rows=1000, **params):
  base_url = os.getenv("GEOSEARCH_API_URL")
  default = {
    'username': GEOKEY_USER,
    'featureCode': feature_codes,
    'maxRows': max_rows,
    'lang': 'en',
    'style':'FULL'
  }
  resp = requests.get(base_url, params={**default, **params})
  resp.raise_for_status()
  if resp.json()['geonames'] == []:
    raise ValueError(f"No results found for {feature_codes} in {params}")
  return pd.json_normalize(resp.json()['geonames'])

def fetch_new_locs(lat,lng):
  base_url = os.getenv("GEONEAR_API_URL")
  params= {
    'username': GEOKEY_USER,
    'lat': lat,
    'lng': lng,
    'maxRows': 1,
  }
  resp = requests.get(base_url, params=params)
  resp.raise_for_status()
  resp_json = resp.json()
  
  return pd.json_normalize(resp_json['geonames'][0])
#Get beach cities in Europe
try:
  beaches = fetch_geo('BCH', max_rows=1000, continentCode='EU')
  beaches = beaches[beaches['countryCode'].isin(EUROPE_CODES)]

  #Get Mountains in Europe
  mountains = fetch_geo('MT', max_rows=1000, continentCode='EU')
  mountains = mountains[mountains['countryCode'].isin(EUROPE_CODES)]

  #Get cities in Europe
  cities = fetch_geo('PPLS', max_rows=1000, continentCode='EU')
  cities = cities[cities['countryCode'].isin(EUROPE_CODES)]

  capital_cities = fetch_geo('PPLC', max_rows=1000, continentCode='EU')
  capital_cities = capital_cities[capital_cities['countryCode'].isin(EUROPE_CODES)]
except Exception as e:
  print(f"Error fetching data from GeoNames: {e}")
  exit(1)
# === 3. Process data ===
beaches_df = pd.DataFrame(beaches).head(round(1000/3)) 
mountains_df = pd.DataFrame(mountains).head(round(1000/3))
capital_cities_df = pd.DataFrame(capital_cities).head(round(1000/3))
print('total beaches: ', len(beaches_df))
print('total mountains: ', len(mountains_df))
print('total capital cities: ', len(capital_cities_df))
print('Fetched locations')
all_locs = pd.concat([beaches_df, mountains_df,capital_cities_df], ignore_index=True)
all_locs = all_locs[['name', 'countryCode', 'lat', 'lng','population']]
# Remove duplicates
print('Total actual locations: ', len(all_locs))
all_locs = all_locs.drop_duplicates(subset=['name', 'countryCode', 'lat', 'lng'], keep='first')
zero_population = all_locs[all_locs['population'] == 0]
print('Removed zero population '+str(len(zero_population)))
#remove zero population
all_locs = all_locs[all_locs['population'] != 0]
print('Total actual locations: ', len(all_locs))
#Search for near locations with population
newLocs = []
print('Get new locations')
try:
  for index, row in zero_population.iterrows():
    lat = float(row['lat'])
    lng = float(row['lng'])
    res = fetch_new_locs(lat,lng)
    newLocs.append(res)
except Exception as e:
  print(f"Error fetching new locations: {e}")
print('Added new locations')
new_locs_df = pd.concat(newLocs, ignore_index=True)
new_locs_df = new_locs_df[['name', 'countryCode', 'lat', 'lng','population']]

new_locs_df = new_locs_df.drop_duplicates(subset=['name', 'countryCode', 'lat', 'lng'], keep='first')
all_locs = pd.concat([all_locs, new_locs_df], ignore_index=True)
#remove zero population
all_locs = all_locs[all_locs['population'] != 0]
print('Total actual locations: ', len(all_locs))
print('Cities total: ', len(cities))
cities_df = pd.DataFrame(cities).head(1000-len(all_locs))
all_locs = pd.concat([all_locs, cities_df], ignore_index=True)
print('Total actual locations: ', len(all_locs))
# Remove duplicates
all_locs = all_locs.drop_duplicates(subset=['name', 'countryCode', 'lat', 'lng'], keep='first')
print('Create timezone')
tf = TimezoneFinder()
all_locs['timezone'] = all_locs.apply(lambda r: tf.timezone_at(lat=float(r.lat), lng=float(r.lng)),axis=1)
all_locs['timezone'] = all_locs['timezone'].astype(str)
# Rename columns
all_locs = all_locs[['name', 'countryCode', 'lat', 'lng','population', 'timezone']]
all_locs = all_locs.rename(
  columns={'name':'name',
            'countryCode':'country_code',
            'lat':'latitude',
            'lng':'longitude'}
)
print('Saved locations on db')
# === 4. Save to SQLite ===
conn = sqlite3.connect('../data/europe_locations.db')
all_locs.to_sql(
    'locations', conn,
    if_exists='replace', index_label='id'
)
conn.close()

print(f"✅ Generated {len(all_locs)} locations in europe_locations.db")
