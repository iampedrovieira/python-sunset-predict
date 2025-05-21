#Made a request to a site and extract all link/src. The links are on the div with class "item". Use Requests libs
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()
import os
def extract_img_urls(url:str)-> list:
  BASE_URL = os.getenv("THIRD_PARTY_SITE")
  
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  item_div = soup.find('div', id='item')
  src_links = []
  if item_div:
      src_links = [img['src'] for img in item_div.find_all('img', src=True)]
      src_links = [link if link.startswith('http') else BASE_URL + link for link in src_links]
  return src_links


def download_img(img_url:str):
  response = requests.get(img_url)
  response.raise_for_status()
  return Image.open(BytesIO(response.content))