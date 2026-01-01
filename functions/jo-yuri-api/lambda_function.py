import json
import common
from model.carousel import Carousel
from model.discography import Discography
from model.gallery import Gallery
from model.video import Video
from DynamoDB import DynamoDB

db = DynamoDB()

def lambda_handler(event, context):
    res = {}
    obj = None
    
    path = event["rawPath"][1:].split("/")[1]
    method = event['requestContext']['http']['method']
    queryStringParameters = event["queryStringParameters"]

    body_raw = event.get('body')
    if body_raw:
        body = json.loads(body_raw)

    match path:
        case "carousel":
            obj = Carousel(db)
        case "discography":
            obj = Discography(db)
        case "gallery":
            obj = Gallery(db)
        case "video":
            obj = Video(db)
        case _:
            return common.res_handler(404, {"errorDescription": "Not Found"})

    match method:
        case "GET":
            status, res = obj.get_handler(queryStringParameters)
        case "POST":
            status, res = obj.post_handler(body)
        case "PUT":
            status, res = obj.put_handler()
        case "DELETE":
            status, res = obj.del_handler(queryStringParameters)
        case _:
            status, res = 405, {"statusDescription": "Method Not Allowed"}

    return common.res_handler(status, res)
