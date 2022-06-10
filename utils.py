import re

import requests
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent


def clean_filename(filename):
    return re.sub(r"[^a-zA-Z0-9\_\-\.]", "_", filename)

class KindPortaalFetcher():
    _session_id: str
    _portal_url: str
    _kind_id: int

    def __init__(self, session_id: str, portal_url: str, kind_id: int) -> None:
        self._session_id = session_id
        self._portal_url = portal_url
        self._kind_id = kind_id
    
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
            'Referer': f'{self._portal_url}/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Pragma': 'no-cache',
        }
    
    def _get_cookies(self):
        return {
            'PHPSESSID': self._session_id,
        }


    def fetch_photo(self, image_url, filename):
        img_data = requests.get(
            f'{self._portal_url}{image_url}',
            cookies=self._get_cookies(),
            headers=self._get_headers()
        ).content
        with open(filename, 'wb') as handler:
            handler.write(img_data)

    def fetch_data(self):
        data = {
            'start': '0',
            'flush': '0',
            'kindId': self._kind_id,
            'filter': 'alles',
        }

        items = {}

        has_more = True

        while has_more:
            response = requests.post(
                f'{self._portal_url}/ouder/tijdlijn/laadtijdlijn',
                cookies=self._get_cookies(),
                headers=self._get_headers(),
                data=data
            ).json()
            print(f"Fetched post {response['data']['start']}-{response['data']['einde']} of {response['data']['totaal']}")
        
            items = items | self._parse_tijdlijn_html(response['data']['html'])
            data['start'] = response['data']['einde']
            if response['data']['einde'] >= response['data']['totaal']:
                has_more = False
        
        return items
    

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
