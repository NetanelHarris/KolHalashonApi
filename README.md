# Kol Halashon API

Python wrapper for Kol Halashon website API.

## Installation
```bash
pip install kolhalashon
```

## Usage
```python
from kolhalashon.api import KolHalashonAPI, QualityLevel
from kolhalashon.models.exceptions import *

from dotenv import load_dotenv


load_dotenv()


api = KolHalashonAPI(
    use_session=False,  
    session_file='session.pkl'
)
category = api.search_items("אברהם")
if category.shiurim:
    print("Shiurim found:")
    for shiur in category.shiurim:
        print(f"shiur: {shiur['SearchItemTextHebrew']}, ID: {shiur['SearchItemId']}")
else:
    print("No shiurim found.")

file_id = category.shiurim[0]['SearchItemId'] 

try:
    file_name = api.download_file(file_id, QualityLevel.AUDIO)
    print(f"Shiur downloaded: {file_name}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except DownloadFailedException as e:
    print(f"Download failed: {e}")
except SessionDisabledException as e:
    print(f"Session disabled: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
```

## Features
- Search shiurim
- Download audio/video content
- Browse by Rabbi