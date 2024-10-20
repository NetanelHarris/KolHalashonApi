# Kol Halashon API

Python wrapper for Kol Halashon website API.

## Installation
```bash
pip install kolhalashon
```

## Usage
```python
from kolhalashon.api import KolHalashonAPI
from kolhalashon.models.exceptions import *
from dotenv import load_dotenv

load_dotenv()

api = KolHalashonAPI(
    use_session=False,  
)


def main():
    search_keyword = "כהן"
    search_results = api.search_items(search_keyword)
    print(search_results)

if __name__ == "__main__":
    main()

```

## Features
- Search shiurim
- Download audio/video content
- Browse by Rabbi