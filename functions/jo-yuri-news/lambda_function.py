from GoogleNews import GoogleNews
from DynamoDB import DynamoDB

# Add zo-glass Layer
# Add Python-requests-bs4 Layer
# Add Python-googlenewsdecoder Layer

db = DynamoDB()

def lambda_handler(event, context):
    GoogleNews(db).start()
    
    return {
        'statusCode': 200,
        'body': "Success",
    }
