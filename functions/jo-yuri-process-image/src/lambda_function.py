import json

import os
import boto3
import io
import urllib.parse
from PIL import Image
import time

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("jo-yuri")

CONFIG = {
    "carousel": {"ratio": (3, 2), "size": (1620, 1080)},
    "discography": {"ratio": (1, 1), "size": (1080, 1080)},
    "gallery": {"ratio": (1, 1), "size": (1080, 1080)},
}

def lambda_handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")

    paths = key.split("/")
        
    resource = paths[1]
    id = paths[-1].split(".")[0]

    response = s3.get_object(Bucket=bucket, Key=key)

    try:
        body = response["Body"].read()
        image = Image.open(io.BytesIO(body))
        image.load()
    except Exception as e:
        print(e)
        setStatus(resource, id, "fail")
        return {
            "statusCode": 422,
            "body": json.dumps("")
        }

    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        composite = Image.alpha_composite(white, rgba)
        image = composite.convert("RGB")
    else:
        image = image.convert("RGB")

    configuration = CONFIG.get(resource)
    image = crop(image, configuration["ratio"])
    image = image.resize(configuration["size"], Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="WEBP")
    buffer.seek(0)

    newKey = f"{resource}/{id}.webp"

    s3.put_object(
        Bucket=bucket,
        Key=newKey,
        Body=buffer,
        ContentType='image/webp'
    )

    setStatus(resource, id, "ready")

    return {
        "statusCode": 200,
        "body": json.dumps("")
    }

def crop(image, ratio):
    w, h = ratio
    ratio = w / h
 
    width, height = image.size
    currentRatio = width / height
 
    if currentRatio > ratio:
        newWidth = round(height * ratio)
        left = (width - newWidth) // 2
        box = (left, 0, left + newWidth, height)
    else:
        newHeight = round(width / ratio)
        top = (height - newHeight) // 2
        box = (0, top, width, top + newHeight)
 
    return image.crop(box)

def setStatus(resource, id, status):
    try:
        table.update_item(
            Key={
                "PK": resource,
                "SK": f"ITEM#{id}"
            },
            UpdateExpression="SET #status = :status, processedAt = :now",
            ConditionExpression="attribute_exists(PK)",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":status": status, ":now": int(time.time())}
        )

        if status == "ready":
            table.update_item(
                Key={
                    "PK": resource,
                    "SK": "METADATA"
                },
                UpdateExpression="ADD countReady :one",
                ExpressionAttributeValues={":one": 1}
            )

    except Exception:
        table.put_item(Item={
            "PK": f"STATUS#{resource}",
            "SK": id,
            "status": status,
            "ttl": int(time.time()) + 60 * 60 * 24
        })
    