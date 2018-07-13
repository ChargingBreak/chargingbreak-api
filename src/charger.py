import json
import os

import boto3


def post(event, context):
    response = {
        "statusCode": 200,
        "body": json.dumps({'data': 'nothing'})
    }

    return response


def get(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['SUPERCHARGERINFO_TABLE'])

    if 'path' in event and 'id' in event['path']:
        item = table.get_item(Key={'id': int(event['path']['id'])})

    return item['Item']


methods = {
    'GET': get,
    'POST': post,
}


def main(event, context):
    if 'method' in event:
        return methods[event['method']](event, context)

    return {"statusCode": 404}
