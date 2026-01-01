from abc import ABC, abstractmethod

class Base(ABC):

    @property
    @abstractmethod
    def PARTITION(self):
        pass

    @property
    @abstractmethod
    def REQUIRED_KEYS(self):
        pass

    @property
    @abstractmethod
    def OPTIONAL_KEYS(self):
        pass

    @property
    @abstractmethod
    def EDITABLE_KEYS(self):
        pass

    @property
    @abstractmethod
    def URL_KEYS(self):
        pass

    def __init__(self, db):
        self.db = db

    def get_handler(self, queryStringParameters=None):
        limit = queryStringParameters.get("limit") or {}
        offset = queryStringParameters.get("offset") or {}
        pageToken = queryStringParameters.get("pageToken") or {}
        return self.db.get_handler(self.PARTITION, limit if limit else 0, offset if offset else 0, pageToken if pageToken else None)

    def post_handler(self, data, user):
        return self.db.post_handler(self.PARTITION, data, user, self.REQUIRED_KEYS, self.OPTIONAL_KEYS, self.URL_KEYS)

    def put_handler(self):
        #TODO
        return 405, {"statusDescription": "Method Not Allowed"}

    def delete_handler(self):
        #TODO
        return 405, {"statusDescription": "Method Not Allowed"}
