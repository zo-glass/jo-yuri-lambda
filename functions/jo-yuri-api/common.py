import json

def res_handler(statusCode, body):
    return {
        'statusCode': statusCode,
        'body': json.dumps(body, default=int),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
