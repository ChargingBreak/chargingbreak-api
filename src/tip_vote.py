import json
import os
import uuid

import boto3
from src import decimalencoder as de


def post(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TIP_VOTES_TABLE'])

    # postBody = json.loads(event['body'])

    responseBody = "Unknown Error"
    statusCode = 200

    try:
        cid = event['pathParameters']['id'] if (
            'pathParameters' in event
            and event['pathParameters']
            and 'id' in event['pathParameters']) else None
        if cid and cid.isdigit():
            response = table.put_item(
                Item={
                    'id': str(uuid.uuid4()),
                    'tip_id': int(cid),
                    'user_id': event['requestContext']['authorizer'
                                                       ]['claims']['sub']
                }
            )

            responseBody = json.dumps(response, cls=de.DecimalEncoder)
        else:
            statusCode = 404
            responseBody = json.dumps({'message': 'Unknown charger'})
    except Exception as e:
        responseBody = json.dumps({'message': str(e)})
        statusCode = 500

    return {
        "statusCode": statusCode,
        "body": responseBody,
        "headers": {
            # TODO: MPN: need to set this for real before live
            # useful to have * for now for local dev
            # 'https://chargingbreak.com'
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
        },
    }


methods = {
    'POST': post,
}


def main(event, context):
    if 'httpMethod' in event:
        return methods[event['httpMethod']](event, context)

    return {
        "statusCode": 404,
        "body": "",
        "headers": {
            # TODO: MPN: need to set this for real before live
            # useful to have * for now for local dev
            # 'https://chargingbreak.com'
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
        },
    }
