import boto3
from boto3.dynamodb.conditions import Key
import time
import secrets

class DynamoDB:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table("jo-yuri")

    def get_handler(self, partition, limit=50, offset=0, exclusiveStartKey=None, filterExpression=None):
        items = []
        lek = exclusiveStartKey

        query_params = {
            "KeyConditionExpression": Key("PK").eq(partition) & Key("SK").begins_with("ITEM#"),
            "ScanIndexForward": False
        }
        
        try:
            if filterExpression:
                query_params["FilterExpression"] = filterExpression

            if offset:
                lek = self.getOffset(offset, query_params)
                if not lek:
                    return {
                        "items": [],
                        "lastEvaluatedKey": None,
                    }

            while len(items) < limit:
                params = dict(query_params)
                params["Limit"] = limit - len(items)
                if lek:
                    params["ExclusiveStartKey"] = lek

                response = self.table.query(**params)
                items.extend(response.get("Items", []))
                lek = response.get("LastEvaluatedKey")

                if not lek:
                    break

            return {
                "items": items[:limit],
                "lastEvaluatedKey": lek,
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
                data["SK"] = self.getSK(pk)
            else:
                if self.skValidator(id, pk):
                    raise ValueError("ID already exists")
                data["SK"] = f"ITEM#{id}"

            self.table.put_item(Item=data)

            isReady = data.get("status") == "ready"
            self.updateCount(pk, countReady=1 if isReady else 0, countTotal=1)

        except Exception as e:
            print(e)
            raise

    def put_handler(self, pk, sk, data):
        try:
            if not self.skValidator(sk, pk):
                raise ValueError("Item not found")

            updateExpression = "SET #updatedAt=:updatedAt"
            expressionAttributeNames = {"#updatedAt": "updatedAt"}
            expressionAttributeValues = {":updatedAt": int(time.time())}

            for key, value in data.items():
                updateExpression += f", #{key}=:{key}"
                expressionAttributeNames[f"#{key}"] = key
                expressionAttributeValues[f":{key}"] = value

            self.table.update_item(
                Key={
                    "PK": pk,
                    "SK": f"ITEM#{sk}"
                },
                UpdateExpression=updateExpression,
                ExpressionAttributeNames=expressionAttributeNames,
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
            expressionAttributeNames = {"#s": "status"}
            expressionAttributeValues = {
                ":status": "deleted",
                ":deletedAt": int(time.time())
            }

            if ttl:
                updateExpression += ", #ttl = :ttl"
                expressionAttributeNames["#ttl"] = "ttl"
                expressionAttributeValues[":ttl"] = int(time.time()) + 60 * 60 * 24 * 365

            response = self.table.update_item(
                Key={
                    "PK": pk,
                    "SK": f"ITEM#{sk}"
                },
                UpdateExpression=updateExpression,
                ExpressionAttributeNames=expressionAttributeNames,
                ExpressionAttributeValues=expressionAttributeValues,
                ReturnValues="ALL_OLD"
            )

            oldItem = response.get("Attributes", {})
            if oldItem.get("status") == "ready":
                self.updateCount(pk, countReady=-1, countTotal=0)

            return oldItem

        except Exception as e:
            print(e)
            raise

    def force_delete_handler(self, pk, sk):
        try:
            if not self.skValidator(sk, pk):
                raise ValueError("Item not found")

            response = self.table.delete_item(
                Key={
                    "PK": pk,
                    "SK": f"ITEM#{sk}"
                },
                ReturnValues="ALL_OLD"
            )

            oldItem = response.get("Attributes", {})
            wasReady = oldItem.get("status") == "ready"
            self.updateCount(pk, countReady=-1 if wasReady else 0, countTotal=-1)

            return oldItem

        except Exception as e:
            print(e)
            raise
    
    def getCount(self, partition, full=False):
        count = 0

        response = self.table.get_item(
            Key={
                "PK": partition,
                "SK": "METADATA"
            }
        )
        item = response.get("Item", {})

        if full:
            count = item.get("countTotal", 0)
        else:
            count = item.get("countReady", 0)

        return count
    
    def updateCount(self, partition, countReady=0, countTotal=0):
        update_expressions = []
        expression_attribute_names = {}
        expression_attribute_values = {}

        if countReady != 0:
            update_expressions.append("#cr :cr")
            expression_attribute_names["#cr"] = "countReady"
            expression_attribute_values[":cr"] = countReady

        if countTotal != 0:
            update_expressions.append("#ct :ct")
            expression_attribute_names["#ct"] = "countTotal"
            expression_attribute_values[":ct"] = countTotal

        update_expression = "ADD " + ", ".join(update_expressions)

        try:
            self.table.update_item(
                Key={
                    "PK": partition,
                    "SK": "METADATA"
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values
            )
        except Exception as e:
            print(e)
            raise
    
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

    def getNextSK(self, partition):
        next = 0
        response = self.table.query(
                    KeyConditionExpression=Key("PK").eq(partition) & Key("SK").begins_with("ITEM#"),
                    ScanIndexForward=False,
                    Limit=1
                ).get("Items")

        if response:
            current = response[0]["SK"].split('#')[-1]
            try:
                next = int(current) + 1
            except ValueError:
                raise ValueError(f"Invalid SK format in partition '{partition}': {current}")

        return f"ITEM#{str(next).zfill(6)}"

    def getSK(self):
        now = int(time.time())
        sufix = secrets.token_hex(8)

        return f"ITEM#{now}{sufix}"

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

    def getStatus(self, partition, id):
        status = "pending"

        try:
            response = self.table.get_item(
                Key={
                    "PK": f"STATUS#{partition}",
                    "SK": id
                }
            )

            item = response.get("Item")
            if item:
                self.table.delete_item(
                    Key={
                        "PK": f"STATUS#{partition}",
                        "SK": id
                    }
                )
                status = item.get("status", "ready")

            return status

        except Exception as e:
            print(e)
            return status
