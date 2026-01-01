from abc import ABC, abstractmethod

import base64
import json
import time
from urllib.parse import urlparse

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

    AUXILIARY_KEYS = ["ttl", "status", "createdBy", "createdAt", "updatedBy", "updatedAt", "deletedBy", "deletedAt"]

    def __init__(self, db):
        self.db = db

    def get_handler(self, queryStringParameters={}, full=False):
        args = {}
        data = {
            "items": [],
            "pageInfo": {},
            "nextPageToken": ""
        }

        limit = queryStringParameters.get("limit", {})
        offset = queryStringParameters.get("offset", {})
        exclusiveStartKey = self.tokenToLek(queryStringParameters.get("pageToken", {}))

        if limit:
            try:
                limit = int(limit)
                if limit < 1 or limit > 50:
                    return 400, {"errorDescription": "limit must be between 1 and 50"}
                args["limit"] = int(limit)
            except Exception as e:
                return 400, {"errorDescription": "limit must be an integer"}

        if offset:
            try:
                offset = int(offset)
                args["offset"] = int(offset)
            except Exception as e:
                return 400, {"errorDescription": "offset must be an integer"}
        
        if exclusiveStartKey:
                args["exclusiveStartKey"] = exclusiveStartKey
        
        try:
            res = self.db.get_handler(self.PARTITION, **args)
        except Exception as e:
            return 500, {"errorDescription": "Internal Server Error"}

        items = res.get("items")
        lek = res.get("lastEvaluatedKey")

        data.update(self.format_items(items, full=full))

        if lek:
            data["nextPageToken"] = self.lekToToken(lek)

        data["pageInfo"]["resultsPerPage"] = len(items)
        data["pageInfo"]["totalResults"] = self.db.getCount(self.PARTITION)
        
        return 200, data

    def get_by_id_handler(self, id, full=False):
        if not id:
            return 400, {"errorDescription": "Missing ID"}

        try:    
            item = self.db.get_by_id_handler(self.PARTITION, id)
        except Exception as e:
            return 500, {"errorDescription": "Internal Server Error"}

        if not item:
            return 404, {"errorDescription": "Item not found"}
        
        return 200, self.format_item(item, full=full)

    def post_handler(self, data, user, ttl=None):
        item = {
            "PK": self.PARTITION,
            "createdAt": int(time.time()),
            "createdBy": user
        }

        missingKeys = self.requiredKeysValidator(data)
        if missingKeys:
            return 400, {"errorDescription": f"Missing {", ".join(missingKeys)} key"}
        
        invalid_urls = self.invalidUrlValidator(data)
        if invalid_urls:
            return 400, {"errorDescription": f"{", ".join(invalid_urls)} invalid URLs"}

        if ttl is not None:
            item["ttl"] = ttl

        for key in self.REQUIRED_KEYS + self.OPTIONAL_KEYS + self.AUXILIARY_KEYS:
                if key in data:
                    item[key] = data[key]

        try:
            self.db.post_handler(self.PARTITION, item)
            return 201, {"statusDescription": "Item Created"}
        except ValueError as e:
            return 409, {"errorDescription": str(e)}
        except Exception as e:
            return 500, {"errorDescription": "Internal Server Error"}

    def put_handler(self, id, data):
        if not id:
            return 400, {"errorDescription": "Missing ID"}

        invalid_urls = self.invalidUrlValidator(data)
        if invalid_urls:
            return 400, {"errorDescription": f"{', '.join(invalid_urls)} invalid URLs"}

        editableData = {}
        failedKeys = []

        for key, value in data.items():
            if key in self.EDITABLE_KEYS:
                editableData[key] = value
            elif key != "id":
                failedKeys.append(key)

        if not editableData:
            return 400, {"errorDescription": "No valid editable keys provided"}

        try:
            self.db.put_handler(self.PARTITION, id, editableData)
        except ValueError as e:
            return 404, {"errorDescription": str(e)}
        except Exception as e:
            return 500, {"errorDescription": "Internal Server Error"}

        description = f"{', '.join(editableData.keys())} successfully edited"
        if failedKeys:
            description += f", {', '.join(failedKeys)} not editable"

        return 200, {"statusDescription": description}

    def delete_handler(self, id, queryStringParameters={}):
        if not id:
            return 400, {"errorDescription": "Missing ID"}

        force = queryStringParameters.get("force") == "true"

        try:
            if force:
                self.db.force_delete_handler(self.PARTITION, id)
            else:
                self.db.delete_handler(self.PARTITION, id)
        except ValueError as e:
            return 404, {"errorDescription": str(e)}
        except Exception as e:
            return 500, {"errorDescription": "Internal Server Error"}

        return 200, {"statusDescription": "Item Deleted"}

    def format_items(self, items, full=False):
        data = {}
        if not full:
            for item in items:
                if item.get("status") == "ready":
                    item["id"] = item["SK"].split('#')[-1]
                    for i in self.AUXILIARY_KEYS:
                        item.pop(i, None)
                    item.pop("PK", None)
                    item.pop("SK", None)
                    data.setdefault("items", []).append(item)
        else:
            for item in items:
                item.pop("PK", None)
                item.pop("SK", None)
                if item.get("status") == "ready":
                    data.setdefault("items", []).append(item)
                elif item.get("status") == "deleted":
                    data.setdefault("deleted", []).append(item)
                else:
                    data.setdefault("other", []).append(item)
        return data

    def format_item(self, item, full=False):
        data = {}
        if item:
            if not full:
                if item.get("status") == "ready":
                    item["id"] = item["SK"].split('#')[-1]
                    for i in self.AUXILIARY_KEYS:
                        item.pop(i, None)
                    item.pop("PK", None)
                    item.pop("SK", None)
                    data = {"item": item}
            else:
                #metadata = {}
                #for k in self.AUXILIARY_KEYS:
                #    metadata[k] = item.pop(k, None)
                #metadata.pop("PK", None)
                #metadata.pop("SK", None)
                #data = {"item": item, "metadata": metadata}
                data = {"item": item}
        return data

    def lekToToken(self, lastEvaluatedKey):
        return base64.b64encode(json.dumps(lastEvaluatedKey).encode('utf-8')).decode('utf-8')

    def tokenToLek(self, token):
        try:
            json_string = base64.b64decode(token).decode('utf-8')
            return json.loads(json_string)
        except Exception as e:
            return None

    def requiredKeysValidator(self, data):
        missingKeys = []

        for key in self.REQUIRED_KEYS:
            if key not in data:
                missingKeys.append(key)

        return missingKeys

    def invalidUrlValidator(self, data):
        invalidUrls = []

        for key in self.URL_KEYS:
            if key in data and not self.urlValidator(data[key]):
                invalidUrls.append(key)

        return invalidUrls

    def urlValidator(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
