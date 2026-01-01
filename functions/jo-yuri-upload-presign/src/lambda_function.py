import json
import boto3
import time
import secrets

s3 = boto3.client("s3")

BUCKET = "jo-yuri"
CDN = "cdn.zo.glass"
TTL = 300

ALLOWED_RESOURCES = ["gallery", "carousel", "discography"]
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_FILE_SIZE = 10 * 1024 * 1024

def lambda_handler(event, context):
    claims = event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {})
    groups = claims.get('cognito:groups', [])

    if isinstance(groups, str):
        groups = [groups]

    if not set(groups) & {"[admin]", "[mod]"}:
        return res_handler(403, {"errorDescription": "Forbidden"})

    body = json.loads(event.get("body", "{}"))
    resource = body.get("resource")
    contentType = body.get("contentType")

    if resource not in ALLOWED_RESOURCES:
        return res_handler(400, {"errorDescription": "Invalid resource"})

    if contentType not in ALLOWED_CONTENT_TYPES:
        return res_handler(400, {"errorDescription": "Invalid contentType"})

    ext = contentType.split("/")[-1]
    now = int(time.time() * 1000)
    sufix = secrets.token_hex(2)
    id = f"{now}{sufix}"
    s3Key = f"uploads/{resource}/{id}.{ext}"

    try:
        '''
        presignedUrl = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET,
                "Key": s3Key,
                "ContentType": contentType
            },
            ExpiresIn=TTL
        )
        '''
        presignedPost = s3.generate_presigned_post(
            Bucket=BUCKET,
            Key=s3Key,
            Fields={
                "Content-Type": contentType
            },
            Conditions=[
                {"Content-Type": contentType},
                ["content-length-range", 1, MAX_FILE_SIZE]
            ],
            ExpiresIn=TTL
        )

    except Exception as e:
        return res_handler(500, {"errorDescription": "Failed to generate presigned URL"})

    #return res_handler(200, {"presignedUrl": presignedUrl, "src": f"https://{CDN}/{resource}/{id}.webp", "id": f"{id}"})
    return res_handler(200, {"presignedPost": presignedPost, "src": f"https://{CDN}/{resource}/{id}.webp", "id": f"{id}"})

def res_handler(statusCode, body):
    return {
        'statusCode': statusCode,
        'body': json.dumps(body, default=int),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
