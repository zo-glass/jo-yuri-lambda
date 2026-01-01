import json

import urllib3
import os

# ADD AWS-Parameters-and-Secrets-Lambda-Extension-Arm64 Layer

http = urllib3.PoolManager()

# Secret Manager cost2much
def getKey(name, ssm=True):
    url = ""
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')}

    if ssm:
        url = f"http://localhost:2773/systemsmanager/parameters/get?name={name}&withDecryption=true"
    else:
        url = f"http://localhost:2773/secretsmanager/get?secretId={name}"

    try:
        res = http.request("GET", url, headers=headers, timeout=3.0)
        if res.status == 200:
            if ssm:
                response = json.loads(res.data.decode("utf-8"))
                return response['Parameter']['Value']
            else:
                data = json.loads(res.data.decode("utf-8"))
                return data.get('SecretString')
    except Exception as e:
        print(f"errorDescription: {e}")
    return None
        
def lambda_handler(event, context):
    res = {
        "isAuthorized": False,
        "context": {}
    }

    try:
        
        if (event["queryStringParameters"]["key"] == getKey("jo-yuri-api-key")):
            res = {
                "isAuthorized": True,
                "context": {}
            }

    except:
        pass

    return res
