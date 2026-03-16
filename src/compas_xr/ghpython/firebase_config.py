class FirebaseConfig:
    """Configuration for Firebase connection.

    Parameters
    ----------
    api_key
        API key for Firebase.
    auth_domain
        Auth domain for Firebase.
    database_url
        URL of the Firebase database.
    storage_bucket
        Storage bucket for Firebase.
    """

    def __init__(self, api_key: str, auth_domain: str, database_url: str, storage_bucket: str):
        self.api_key = api_key
        self.auth_domain = auth_domain
        self.database_url = database_url
        self.storage_bucket = storage_bucket

    def __str__(self) -> str:
        return f"FirebaseConfig, api_key={self.api_key}, auth_domain={self.auth_domain}, database_url={self.database_url}, storage_bucket={self.storage_bucket}"

    def __data__(self) -> dict:
        return {
            "apiKey": self.api_key,
            "authDomain": self.auth_domain,
            "databaseURL": self.database_url,
            "storageBucket": self.storage_bucket,
        }
