import json
import common
from model.carousel import Carousel
from model.discography import Discography
from model.gallery import Gallery
from model.video import Video
from model.news import News
from model.schedule import Schedule
from DynamoDB import DynamoDB

# Add zo-glass Layer

db = DynamoDB()

def lambda_handler(event, context):
    res = {}
    obj = None
    queryStringParameters = None
    body = None
    
    
    method = event.get('requestContext', {}).get('http', {}).get('method')
    id = event.get("pathParameters", {}).get("id", {})

    path = event.get("rawPath", "/")
    isAdmin = "/admin/" in path

    resource = None
    stage = event.get("requestContext", {}).get("stage", "")
    for i in path.split("/"):
        if i and i != stage and i != "admin":
            resource = i
            break

    claims = event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {})
    username = claims.get('cognito:username') or claims.get('username')
    groups = claims.get('cognito:groups', [])
    if isinstance(groups, str):
        groups = [groups]
    groups = set(groups)

    queryStringParameters = event.get('queryStringParameters') 
    if not queryStringParameters:
        queryStringParameters = {}

    body_raw = event.get('body')
    if body_raw:
        body = json.loads(body_raw)

    match resource:
        case "carousel":
            obj = Carousel(db)
        case "discography":
            obj = Discography(db)
        case "gallery":
            obj = Gallery(db)
        case "video":
            obj = Video(db)
        case "news":
            obj = News(db)
        case "schedule":
            obj = Schedule(db)
        case _:
            status, res = 404, {"errorDescription": "Not Found"}

    match method:
        case "GET":
            if id:
                status, res = obj.get_by_id_handler(id, full=isAdmin)
            else:
                status, res = obj.get_handler(queryStringParameters, full=isAdmin)
        case "POST" if isAdmin and groups & {"[admin]", "[mod]"}:
            status, res = obj.post_handler(body, username)
        case "PUT" if isAdmin and groups & {"[admin]", "[mod]"}:
            status, res = obj.put_handler(id, body)
        case "DELETE" if isAdmin and groups & {"[admin]"}:
            status, res = obj.delete_handler(id, queryStringParameters)
        case _:
            status, res = 405, {"statusDescription": "Method Not Allowed"}

    return common.res_handler(status, res)
