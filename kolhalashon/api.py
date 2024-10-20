import os
from dotenv import load_dotenv
from typing import List, Dict, Generator

from sympy import Li
from .models.shiur import Shiur, ShiurDetails, QualityLevel
from .models.exceptions import *
from .utils.session_manager import SessionManager

load_dotenv()

class KolHalashonAPI:
    def __init__(self, username: str = None, password: str = None, use_session=False, session_file='session.pkl'):
        self.username = username if username else os.getenv('KOL_HALASHON_USERNAME', '')
        self.password = password if password else os.getenv('KOL_HALASHON_PASSWORD', '')
        self._base_url = "https://www2.kolhalashon.com:444/api/"
        self._headers = {
            'origin': 'https://www2.kolhalashon.com',
            'referer': 'https://www2.kolhalashon.com/',
        }
        
        self.use_session = use_session
        self.session_manager = SessionManager(session_file)
        
        if self.use_session:
            self._init_session()

    def _init_session(self):
        try:
            self.session_manager.load_session()
            if not self.session_manager.is_token_valid():
                raise SessionNotLoadedException()
        except SessionNotLoadedException:
            print("Session not found or invalid, attempting to login.")
            self.__login(self.username, self.password)

    def __login(self, username: str, password: str):
        if not username or not password:
            raise AuthenticationError("Username and password are required")

        login_url = f"{self._base_url}Accounts/UserLogin/"
        payload = {"Username": username, "Password": password}
        response = self.session_manager.session.post(login_url, json=payload, headers=self._headers)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('Token')
            if token:
                self.session_manager.set_tokens(token, data.get('SiteKey', ''))
                return True
            raise AuthenticationError("Login successful but no token found")
        raise AuthenticationError(f"Login failed with status code {response.status_code}")


    def search_items(self, keyword: str, user_id: int = -1) -> List[Dict]:
        url = f"{self._base_url}Search/WebSite_GetSearchItems/{keyword}/{user_id}/1/4"
        response = self.session_manager.session.get(url, headers=self._headers)
        if response.status_code == 200:
            return response.json()  # Return the items directly
        else:
            print(f"Request failed with status code {response.status_code} and response: {response.text}")
            raise SearchFailedException(f"Error fetching data for keyword: {keyword}", response.status_code)


    def search_rav_shiurim(self, rav_id: int) -> Generator[Shiur, None, None]:
        url = f"{self._base_url}Search/WebSite_GetRavShiurim/"
        data = {
            "QueryType": -1,
            "LangID": -1,
            "MasechetID": -1,
            "DafNo": -1,
            "FromRow": 0,
            "NumOfRows": 24,
            "GeneralID": rav_id,
            "FilterSwitch": "1" * 90
        }
        response = self.session_manager.session.post(url, headers=self.session_manager.headers, json=data)
        if response.status_code == 200:
            yield from self.format_shiurim(response.json())
        else:
            raise SearchFailedException(f"Error fetching Rav Shiurim for Rav ID: {rav_id}", response.status_code)


    def download_file(self, file_id: int, quality_level: QualityLevel) -> str:
        if not self.use_session:
            raise SessionDisabledException()

        download_key = self.session_manager.get_download_key(file_id)
        url = f"{self._base_url}files/GetFileDownload/{file_id}/{quality_level.value}/{download_key}/null/false/false"
        print(url)
        file_extension = 'mp3' if quality_level == QualityLevel.AUDIO else 'mp4'
        quality_name = 'audio' if quality_level == QualityLevel.AUDIO else 'video' if quality_level == QualityLevel.VIDEO else 'hd'
        file_name = f"shiur_{file_id}_{quality_name}.{file_extension}"

        response = self.session_manager.session.get(url, headers=self.session_manager.headers, stream=True)
        if response.status_code == 200:
            with open(file_name, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return file_name
        raise DownloadFailedException("Download failed", response.status_code, file_id, quality_level)



    def get_shiur_details(self, file_id: int) -> ShiurDetails:
        url = f"{self._base_url}TblShiurimLists/WebSite_GetShiurDetails/{file_id}"
        response = self.session_manager.session.get(url, headers=self.session_manager.headers)
        
        if response.status_code == 200:
            return self._parse_shiur_details(response.json())
        raise ShiurDetailsNotFoundException(file_id)
    


    @staticmethod
    def format_shiurim(shiurim: List[Dict]) -> Generator[Shiur, None, None]:
        for shiur in shiurim:
            yield Shiur(
                file_id=shiur.get("FileId", 0),
                title=shiur.get("TitleHebrew", ""),
                rav=shiur.get("UserNameHebrew", ""),
                duration=shiur.get("ShiurDuration", "Unavailable"),
                record_date=shiur.get("RecordDate", ""),
                main_topic=shiur.get("MainTopicHebrew", ""),
                category_1=shiur.get("CatDesc1", ""),
                category_2=shiur.get("CatDesc2", ""),
                audio_available=shiur.get("HasAudio", False),
                video_available=shiur.get("HasVideo", False),
                hd_video_available=shiur.get("HasHdVideo", False),
                download_count=shiur.get("DownloadCount", 0),
                women_only=shiur.get("IsWomenOnly", False),
                shiur_type=shiur.get("ShiurType", "Unavailable"),
                viewed_by_user=shiur.get("ViewdByUser", False)
            )
            
    @staticmethod
    def _parse_shiur_details(data: Dict) -> ShiurDetails:
        return ShiurDetails(
            file_id=data.get("FileId", 0),
            title=data.get("TitleHebrew", ""),
            rav=data.get("UserNameHebrew", ""),
            duration=data.get("ShiurDuration", "Unavailable"),
            record_date=data.get("RecordDate", ""),
            main_topic=data.get("MainTopicHebrew", ""),
            audio_available=data.get("HasAudio", False),
            video_available=data.get("HasVideo", False),
            hd_video_available=data.get("HasHdVideo", False),
            categories=[data.get("CatDesc1", ""), data.get("CatDesc2", "")]
        )
