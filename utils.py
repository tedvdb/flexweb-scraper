import re
from datetime import date, datetime

import piexif
import requests
from bs4 import BeautifulSoup
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

    def _get_headers(self):
        user_agent_rotator = UserAgent()
        user_agent = user_agent_rotator.get_random_user_agent()
        return {
            'User-Agent': user_agent,
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

        exif_dict = piexif.load(filename)
        piexif.remove(filename)
        exif_dict['0th'][piexif.ImageIFD.DateTime] = creation_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = creation_date
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = creation_date
        exif_bytes = piexif.dump(filename)
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
            print(f"Found {len(photos)} in {year}-{month}")
        return photos

    @staticmethod
    def _parse_tijdlijn_html(data: str):
        result = {}
        soup = BeautifulSoup(data, features='lxml')
        for item in soup.find_all('div', class_='tijdlijn-item'):
            datum = item.find('div', class_='tijd-lijn-tijddatum')
            if datum is None:
                datum = "Onbekend"
            else:
                datum = datum.string
            for tijdlijn_foto in item.find_all('div', class_='tijd-lijn-foto'):
                photos = []
                for foto in tijdlijn_foto.find_all('a'):
                    photos.append(foto['href'])
                result[datum] = photos
        return result
