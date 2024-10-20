import pickle
import os
import logging
import requests
from typing import Optional
from urllib.parse import urljoin
from ..models.exceptions import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    BASE_URL = "https://www2.kolhalashon.com:444/api"
    
    def __init__(self, session_file: str = 'session.pkl'):
        self.session_file = session_file
        self.session = requests.Session()
        self.auth_token: Optional[str] = None
        self.site_key: Optional[str] = None
        self._setup_default_headers()

    def _setup_default_headers(self) -> None:
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'origin': 'https://www2.kolhalashon.com',
            'referer': 'https://www2.kolhalashon.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def load_session(self) -> None:
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'rb') as file:
                    data = pickle.load(file)
                    self.session.cookies.update(data.get('cookies', {}))
                    self.auth_token = data.get('auth_token')
                    self.site_key = data.get('site_key')
                    self.headers.update(data.get('headers', {}))
                    self._update_auth_headers()
                    logger.info("Session loaded from file")
            except Exception as e:
                logger.warning(f"Failed to load session file: {e}")
                self._initialize_empty_session()
        else:
            logger.info("No session file found, initializing empty session")
            self._initialize_empty_session()
    
    def _initialize_empty_session(self) -> None:
        self.session.cookies.clear()
        self._setup_default_headers()
        logger.debug("Empty session initialized")
            
    def save_session(self) -> None:
        session_data = {
            'cookies': self.session.cookies.get_dict(),
            'auth_token': self.auth_token,
            'site_key': self.site_key,
            'headers': self.headers
        }
        with open(self.session_file, 'wb') as file:
            pickle.dump(session_data, file)
        logger.info("Session saved successfully")

    def _update_auth_headers(self) -> None:
        if self.auth_token:
            self.headers['authorization'] = f'Bearer {self.auth_token}'
        if self.site_key:
            self.headers['authorization-site-key'] = f'Bearer {self.site_key}'

    def get_download_key(self, file_id: int) -> str:
        url = urljoin(self.BASE_URL, f"api/files/checkAutorizationDownload/{file_id}/false")

        response = self._send_request('GET', url)
        response.raise_for_status()
        
        data = response.json()
        key = data.get('key')
        if not key:
            raise DownloadKeyNotFoundException(file_id)
        return key

    def _send_request(self, method: str, url: str, **kwargs) -> requests.Response:
        kwargs['headers'] = self.headers
        response = self.session.request(method, url, **kwargs)
        self.session.cookies.update(response.cookies)
        self.save_session()
        return response

    def is_token_valid(self) -> bool:
        try:
            self.get_download_key(30413171)  # Test file ID
            return True
        except Exception:
            return False
        
    def set_tokens(self, auth_token: str, site_key: str) -> None:
        self.auth_token = auth_token
        self.site_key = site_key
        if auth_token:
            self.headers['authorization'] = f'Bearer {auth_token}'
        if site_key:
            self.headers['authorization-site-key'] = f'Bearer {site_key}'
        self.save_session()