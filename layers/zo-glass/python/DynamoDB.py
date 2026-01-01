import boto3
from boto3.dynamodb.conditions import Key
import time

class DynamoDB:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table("jo-yuri")

    def get_handler(self, partition, limit=50, offset=0, exclusiveStartKey=None):
        query_params = {
            "KeyConditionExpression": Key("PK").eq(partition) & Key("SK").begins_with("ITEM#"),
            "ScanIndexForward": False
        }
        
        try:
            if limit:
                query_params['Limit'] = limit

            if exclusiveStartKey:
                query_params['ExclusiveStartKey'] = exclusiveStartKey

            if offset:
                lek = self.getOffset(offset, query_params)
                if lek:
                    query_params['ExclusiveStartKey'] = lek
                else:
                    return {
                        "items": [],
                        "lastEvaluatedKey": None,
                    }
                
            response = self.table.query(**query_params)

            return {
                "items": response.get("Items", []),
                "lastEvaluatedKey": response.get("LastEvaluatedKey"),
            }

        except Exception as e:
            print(e)
            raise

    def get_by_id_handler(self, partition, id):
        query_params = {
            "KeyConditionExpression": Key("PK").eq(partition) & Key("SK").eq(f"ITEM#{id}"),
        }
        
        try:
            response = self.table.query(**query_params)

            item = response.get("Items")

            if item:
                item = item[0]

            return item

        except Exception as e:
            print(e)
            raise

    def get_by_prefix_handler(self, partition, prefix):
        query_params = {
            "KeyConditionExpression": Key("PK").eq(partition) & Key("SK").begins_with(f"ITEM#{prefix}"),
            "ScanIndexForward": False
        }
        
        try:
            response = self.table.query(**query_params)

            return {
                "items": response.get("Items", []),
                "lastEvaluatedKey": response.get("LastEvaluatedKey"),
            }

        except Exception as e:
            print(e)
            raise

    def get_by_range_handler(self, partition, start, end, pageToken=None):
        sk_start = f"ITEM#{start}"
        sk_end = f"ITEM#{end}\uffff"

        query_params = {
            "KeyConditionExpression": Key("PK").eq(partition) & Key('SK').between(sk_start, sk_end),
            "ScanIndexForward": False
        }
        
        try:
            if pageToken:
                query_params['ExclusiveStartKey'] = pageToken

            response = self.table.query(**query_params)

            return {
                "items": response.get("Items", []),
                "lastEvaluatedKey": response.get("LastEvaluatedKey"),
            }
        
        except Exception as e:
            print(e)
            raise

    def post_handler(self, pk, data):
        try:
            id = data.get("id")
            if not id:
                data["SK"] = self.getNexttSK(pk)
            else:
                if self.skValidator(id, pk):
                    raise ValueError("ID already exists")
                data["SK"] = f"ITEM#{id}"

            self.table.put_item(Item=data)

        except Exception as e:
            print(e)
            raise

    def put_handler(self, pk, sk, data):
        try:
            if not self.skValidator(sk, pk):
                raise ValueError("Item not found")

            updateExpression = "SET updatedAt=:updatedAt"
            expressionAttributeValues = {":updatedAt": int(time.time())}

            for key, value in data.items():
                updateExpression += f", {key}=:{key}"
                expressionAttributeValues[f":{key}"] = value

            self.table.update_item(
                Key={
                    "PK": pk,
                    "SK": f"ITEM#{sk}"
                },
                UpdateExpression=updateExpression,
                ExpressionAttributeValues=expressionAttributeValues,
                ReturnValues="UPDATED_NEW"
            )

        except Exception as e:
            print(e)
            raise
            
    def delete_handler(self, pk, sk, ttl=True):
        try:
            if not self.skValidator(sk, pk):
                raise ValueError("Item not found")

            updateExpression = "SET #s = :status, deletedAt = :deletedAt"
            expressionAttributeValues = {
                ":status": "deleted",
                ":deletedAt": int(time.time())
            }

            if ttl:
                updateExpression += ", ttl = :ttl"
                expressionAttributeValues[":ttl"] = int(time.time()) + 60 * 60 * 24 * 365

            self.table.update_item(
                Key={
                    "PK": pk,
                    "SK": f"ITEM#{sk}"
                },
                UpdateExpression=updateExpression,
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues=expressionAttributeValues,
            )

        except Exception as e:
            print(e)
            raise

    def force_delete_handler(self, pk, sk):
        try:
            if not self.skValidator(sk, pk):
                raise ValueError("Item not found")

            self.table.delete_item(
                Key={
                    "PK": pk,
                    "SK": f"ITEM#{sk}"
                }
            )

        except Exception as e:
            print(e)
            raise
    
    def getCount(self, partition):
        response = self.table.get_item(
            Key={
                "PK": partition,
                "SK": "METADATA"
            }
        )
        return response.get("Item", {}).get("count", 0)
    
    def getCountByRange(self, partition, sk_start, sk_end):
        count = 0

        query_params = {
            "KeyConditionExpression": Key("PK").eq(partition) & Key("SK").between(sk_start, sk_end),
            "ScanIndexForward": False,
            "Select": "COUNT",
        }

        while True:
            response = self.table.query(**query_params)
            count += response["Count"]

            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break
            query_params["ExclusiveStartKey"] = last_key

        return count
    
    def getCountByPrefix(self, partition, prefix):
        count = 0

        query_params = {
            "KeyConditionExpression": Key("PK").eq(partition) & Key("SK").begins_with(f"ITEM#{prefix}"),
            "ScanIndexForward": False,
            "Select": "COUNT",
        }

        while True:
            response = self.table.query(**query_params)
            count += response["Count"]

            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break
            query_params["ExclusiveStartKey"] = last_key

        return count

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

    def getNexttSK(self, partition):
        next = 0
        response = self.table.query(
                    KeyConditionExpression=Key("PK").eq(partition) & Key("SK").begins_with("ITEM#"),
                    ScanIndexForward=False,
                    Limit=1
                ).get("Items")

        if response:
            current = response[0]["SK"].split('#')[-1]
            next = int(current) + 1

        return f"ITEM#{str(next).zfill(6)}"

    def skValidator(self, sk, pk):
        if sk is None:
            return False

        response = self.table.get_item(
            Key={
                "PK": pk,
                "SK": f"ITEM#{sk}"
            }
        )

        if not response.get("Item"):
            return False

        return True
