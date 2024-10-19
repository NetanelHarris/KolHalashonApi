class SessionDisabledException(Exception):
    def __init__(self, message="Session is disabled. Please enable session by setting `use_session=True` to download the file."):
        self.message = message
        super().__init__(self.message)

class AuthenticationError(Exception):
    def __init__(self, message="Authentication failed. Please check your credentials."):
        self.message = message
        super().__init__(self.message)

class TokenExpiredException(Exception):
    def __init__(self, message="Token expired. Please login again."):
        self.message = message
        super().__init__(self.message)

class DownloadKeyNotFoundException(Exception):
    def __init__(self, file_id):
        self.message = f"Download key for file ID {file_id} was not found."
        super().__init__(self.message)

class ShiurDetailsNotFoundException(Exception):
    def __init__(self, file_id):
        self.message = f"Details for Shiur with file ID {file_id} were not found."
        super().__init__(self.message)

class SessionNotLoadedException(Exception):
    def __init__(self, message="Session file not found or failed to load."):
        self.message = message
        super().__init__(self.message)

class SearchFailedException(Exception):
    def __init__(self, message, status_code):
        self.message = f"Search failed with status code {status_code}: {message}"
        super().__init__(self.message)

class DownloadFailedException(Exception):
    def __init__(self, message, status_code, file_id, quality_level):
        self.message = message
        self.status_code = status_code
        self.file_id = file_id
        self.quality_level = quality_level
        super().__init__(self.message)