import json
import os

import boto3
from src import decimalencoder as de


def post(event, context):
    response = {
        "statusCode": 200,
        "body": json.dumps({'data': 'nothing'})
    }

    return response


def get(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['SUPERCHARGERINFO_TABLE'])

    body = "Unknown Error"
    statusCode = 200

    try:
        if ('pathParameters' in event
            and event['pathParameters']
                and 'id' in event['pathParameters']):
            item = table.get_item(
                Key={'id': int(event['pathParameters']['id'])})
            body = json.dumps(item['Item'], cls=de.DecimalEncoder)
        else:
            statusCode = 510  # not extended.
            # Further extensions to the request are required
            # for the server to fulfill it.

            body = json.dumps(
                {'message': 'unable to fulfill request at this time'})
    except Exception as e:
        body = json.dumps({'message': str(e)})
        statusCode = 500

    return {
        "statusCode": statusCode,
        "body": body
    }


methods = {
    'GET': get,
    'POST': post,
}


def main(event, context):
    if 'httpMethod' in event:
        return methods[event['httpMethod']](event, context)

    return {"statusCode": 404}
