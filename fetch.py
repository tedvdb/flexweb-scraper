import os

from decouple import config
from tqdm import tqdm

from utils import KindPortaalFetcher, clean_filename

SESSID = config('SESSID')
BASE_URL = config('BASE_URL')
KIND_ID = config('KIND_ID', cast=int)

OUTPUT_FOLDER = f'output/{KIND_ID}/'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

kpf = KindPortaalFetcher(SESSID, BASE_URL, KIND_ID)

items = kpf.fetch_data()
for post_date in tqdm(items):
    photos = items[post_date]
    base_filename = f'{OUTPUT_FOLDER}'+clean_filename(post_date)
    for photo in photos:
        number = photo.rsplit('/', 1)[-1]
        filename = base_filename+f'_{number}.jpg'
        if not os.path.exists(filename):
            kpf.fetch_photo(photo, filename)
