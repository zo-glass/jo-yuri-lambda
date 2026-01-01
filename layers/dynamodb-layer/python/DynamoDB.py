import boto3
from boto3.dynamodb.conditions import Key

import time
from urllib.parse import urlparse
import base64
import json

class DynamoDB:
    AUXILIARY_KEYS = ["ttl", "status", "createdBy", "createdAt", "updatedBy", "updatedAt", "deletedBy", "deletedAt"]
    MAX_ITEMS = 999

    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table("jo-yuri")

    def get_handler(self, partition, limit=0, offset=0, pageToken=None, full=False):
        query_params = {
            "KeyConditionExpression": Key("PK").eq(partition) & Key("SK").begins_with("ITEM"),
            "ScanIndexForward": False
        }
        
        try:
            limit = int(limit)
            offset = int(offset)
            data = {}

            if limit:
                if limit > self.MAX_ITEMS:
                    return 400, {"errorDescription": f"Limit must be less than {self.MAX_ITEMS}"}
                else:
                    query_params['Limit'] = limit
            else:
                query_params['Limit'] = self.MAX_ITEMS

            if pageToken:
                lek = self.tokenToLek(pageToken)
                if lek:
                    query_params['ExclusiveStartKey'] = lek
                else:
                    return 400, {"errorDescription": "Invalid page token"}

            data.setdefault("pageInfo", {})["totalResults"] = self.getCount(partition)

            if offset and not pageToken:
                lek = self.getOffset(offset, query_params)
                if lek:
                    query_params['ExclusiveStartKey'] = lek
                else:
                    data["items"] = []
                    data["pageInfo"]["resultsPerPage"] = 0
                    return 200, data
                
            response = self.table.query(**query_params)

            items = response.get("Items")

            if not full:
                for item in items:
                    if item.get("status") == "ready":
                        for i in self.AUXILIARY_KEYS:
                            item.pop(i, None)
                        data.setdefault("items", []).append(item)
            else:
                for item in items:
                    if item.get("status") == "ready":
                        data.setdefault("items", []).append(item)
                    elif item.get("status") == "deleted":
                        data.setdefault("deleted", []).append(item)
                    else:
                        data.setdefault("other", []).append(item)

            lastEvaluatedKey = response.get("LastEvaluatedKey")
            if lastEvaluatedKey:
                data["nextPageToken"] = self.lekToToken(lastEvaluatedKey)

            data.setdefault("pageInfo", {})["resultsPerPage"] = len(data.get("items", []))

            return 200, data

        except Exception as e:
            print(e)
            return 500, {"errorDescription": str(e)}

    def idValidator(self, id, partition):
        if id is None:
            return False

        response = self.table.get_item(
            Key={
                "PK": partition,
                "SK": id
            }
        )

        if not response.get("Item"):
            return False

        return True

    def getCount(self, partition):
        response = self.table.get_item(
            Key={
                "PK": partition,
                "SK": "METADATA"
            }
        )
        return response.get("Item", {}).get("count", 0)

    def lekToToken(self, lastEvaluatedKey):
        return base64.b64encode(json.dumps(lastEvaluatedKey).encode('utf-8')).decode('utf-8')

    def tokenToLek(self, token):
        try:
            json_string = base64.b64decode(token).decode('utf-8')
            return json.loads(json_string)
        except Exception as e:
            return None

    def getOffset(self, offset, query_params):
        skip = query_params.copy()
        count = 0
        lek = None

        while count < offset:

            skip['Limit'] = offset - count

            if lek:
                skip['ExclusiveStartKey'] = lek
            res = self.table.query(**skip)
            count += res.get("Count")
            lek = res.get("LastEvaluatedKey")

            if not lek:
                break

        return lek

    def requiredKeysValidator(self, data, requiredKeys):
        missingKeys = []

        for key in requiredKeys:
            if key not in data:
                missingKeys.append(key)

        return missingKeys

    def invalidUrlValidator(self, data, urlKeys):
        invalidUrls = []

        for key in urlKeys:
            if key in data and not self.urlValidator(data[key]):
                invalidUrls.append(key)

        return invalidUrls

    def urlValidator(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
