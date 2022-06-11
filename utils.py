import re
from datetime import date, datetime

import piexif
import requests
from dateutil.rrule import MONTHLY, rrule
from random_user_agent.user_agent import UserAgent


def clean_filename(filename):
    return re.sub(r"[^a-zA-Z0-9\_\-\.]", "_", filename)


def months(start: date):
    now = datetime.now()
    end = datetime(now.year, now.month, 1)
    return [(d.month, d.year) for d in rrule(MONTHLY, dtstart=start, until=end)]


class KindPortaalFetcher():
    _session_id: str
    _portal_url: str
    _start_date: date

    def __init__(self, session_id: str, portal_url: str, start_date: date) -> None:
        self._session_id = session_id
        self._portal_url = portal_url
        self._start_date = start_date
        user_agent_rotator = UserAgent()
        self._user_agent = user_agent_rotator.get_random_user_agent()

    def _get_headers(self):
        return {
            'User-Agent': self._user_agent,
            'Accept': '*/*',
            'Accept-Language': 'nl,en-US;q=0.7,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cache-Control': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': self._portal_url,
            'Connection': 'keep-alive',
            'Referer': f'{self._portal_url}/ouder/fotoalbum',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Pragma': 'no-cache',
        }

    def _get_cookies(self):
        return {
            'PHPSESSID': self._session_id,
        }

    def fetch_photo_meta(self, photo_id):
        data = {
            'id': photo_id,
        }
        response = requests.post(
            f'{self._portal_url}/ouder/fotoalbum/fotometa',
            cookies=self._get_cookies(),
            headers=self._get_headers(),
            data=data
        ).json()
        return response[0]

    def fetch_photo(self, image_id, filename, creation_date):
        img_data = requests.get(
            f'{self._portal_url}/ouder/media/mediajpg/media/{image_id}/formaat/groot/vierkant/0',
            cookies=self._get_cookies(),
            headers=self._get_headers()
        ).content
        with open(filename, 'wb') as handler:
            handler.write(img_data)
        self.update_exif_date(filename, creation_date)

    @staticmethod
    def update_exif_date(filename, creation_date):
        exif_dict = piexif.load(filename)

        piexif.remove(filename)

        new_exif_date = creation_date.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict['0th'][piexif.ImageIFD.DateTime] = new_exif_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_exif_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_exif_date
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)

    def fetch_image_id_list(self):
        photos = []

        for month, year in months(self._start_date):
            data = {
                'year': year,
                'month': month,
            }
            response = requests.post(
                f'{self._portal_url}/ouder/fotoalbum/standaardalbum',
                cookies=self._get_cookies(),
                headers=self._get_headers(),
                data=data
            ).json()
            photos = photos + response['FOTOS']
            print(f"Found {len(photos)} photos  ({year}-{month})")
        return photos
