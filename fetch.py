import os
from datetime import datetime

from decouple import config
from tqdm import tqdm

from utils import KindPortaalFetcher, clean_filename

SESSID = config('SESSID')
BASE_URL = config('BASE_URL')
START_MONTH = config('START_MONTH')

try:
    start_date = datetime.strptime(START_MONTH, '%Y-%m')
except:
    print("Invalid START_MONTH (try something like 2020-01)")
    exit(1)

OUTPUT_FOLDER = 'output/'

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

kpf = KindPortaalFetcher(SESSID, BASE_URL, start_date)

photos = kpf.fetch_image_id_list()
for photo_id in tqdm(photos):
    meta = kpf.fetch_photo_meta(photo_id)
    filename = f'{OUTPUT_FOLDER}'+clean_filename(photo_id)+'.jpg'
    if not os.path.exists(filename):
        kpf.fetch_photo(photo_id, filename, meta['MEDIA_DAG'])
