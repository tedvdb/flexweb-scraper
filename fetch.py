import os
from datetime import datetime

from decouple import config
from tqdm.contrib.concurrent import thread_map

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


def process_photo(photo_id):
    meta = kpf.fetch_photo_meta(photo_id)
    date_created = meta['MEDIA_DAG']  # 2022-06-10T13:20:39
    date_created = datetime.strptime(date_created, '%Y-%m-%dT%H:%M:%S')

    filename = f'{OUTPUT_FOLDER}'+clean_filename(photo_id)+'.jpg'
    if not os.path.exists(filename):
        kpf.fetch_photo(photo_id, filename, date_created)


thread_map(
    process_photo,
    photos,
    max_workers=4
)
