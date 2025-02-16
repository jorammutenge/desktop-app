import os
import requests
from duckduckgo_search import DDGS
import polars as pl

# List of actresses
df = pl.read_parquet('data/movie_shows.parquet')

actress_list = (df
 .select('Person')
 .with_columns(pl.col('Person').str.split(' | '))
 .explode('Person')
 .unique()
 ['Person'].to_list()
 )

# Create directory to store images
os.makedirs("actress_images", exist_ok=True)

def download_image(query, save_path):
    with DDGS() as ddgs:
        results = list(ddgs.images(query, max_results=1))
    
    if results:
        image_url = results[0]["image"]
        image_data = requests.get(image_url).content
        with open(save_path, "wb") as f:
            f.write(image_data)
        print(f"Downloaded: {save_path}")
    else:
        print(f"No image found for {query}")

# Download images
for actress in actress_list:
    file_name = f"actress_images/{actress.replace(' ', '_')}.jpg"
    download_image(actress, file_name)
