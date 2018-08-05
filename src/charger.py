import json
import os

import boto3
from boto3.dynamodb.conditions import Attr, Key
from src import decimalencoder as de


def post(event, context):
    response = {
        "statusCode": 200,
        "body": json.dumps({'data': 'nothing'}),
        "headers": {
            # TODO: MPN: need to set this for real before live
            # useful to have * for now for local dev
            # 'https://chargingbreak.com'
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
        },
    }

    return response


def get_tips(charger_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    tips_table = dynamodb.Table(os.environ['TIPS_TABLE'])

    try:
        tips = tips_table.query(
            KeyConditionExpression=Key('charger_id').eq(int(charger_id)),
            IndexName='charger_id-index'
        )
    except Exception as e:
        return []
    else:
        return tips['Items']


def get_ratings_default():
    return [{
        'theme': category.strip(),
        'rating': 0
    } for category in os.environ['RATING_TYPES'].split(',')]


def get(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(os.environ['CHARGERS_TABLE'])

    body = "Unknown Error"
    statusCode = 200

    try:
        cid = event['pathParameters']['id'] if (
            'pathParameters' in event
            and event['pathParameters']
            and 'id' in event['pathParameters']) else None
        if cid and cid.isdigit():
            item = table.get_item(
                Key={'id': int(cid)})

            if item and 'Item' in item:
                data = item['Item']

                # load up tips!
                data['tips'] = get_tips(data['id'])

                # load up ratings if not present
                if 'ratings' not in data:
                    data['ratings'] = get_ratings_default()

                body = json.dumps(data, cls=de.DecimalEncoder)
            else:
                body = 'Invalid Charger Id'
        else:
            params = {
                'TableName': os.environ['CHARGERS_TABLE'],
                'IndexName': 'status-index',
            }

            if not cid:
                cid = 'OPEN'

            if cid != 'ALL':
                params['FilterExpression'] = Attr('status').eq(cid)

            response = table.scan(**params)
            body = json.dumps(response['Items'], cls=de.DecimalEncoder)
    except Exception as e:
        body = json.dumps({'message': str(e)})
        statusCode = 500

    return {
        "statusCode": statusCode,
        "body": body,
        "headers": {
            # TODO: MPN: need to set this for real before live
            # useful to have * for now for local dev
            # 'https://chargingbreak.com'
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
        },
    }


methods = {
    'GET': get,
    'POST': post,


}


def main(event, context):
    if 'httpMethod' in event and event['httpMethod'] in methods:
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
