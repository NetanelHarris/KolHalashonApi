from typing import Optional, TypedDict


class SessionData(TypedDict):
    cookies: dict[str, str]
    auth_token: Optional[str]
    site_key: Optional[str]
    headers: dict[str, str]
