from YouTube import YouTube
from DynamoDB import DynamoDB

db = DynamoDB()

def lambda_handler(event, context):
    YouTube(db).start()

    return {
        'statusCode': 200,
        'body': "Success",
    }
