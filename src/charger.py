import json
import os

import boto3
from boto3.dynamodb.conditions import Attr
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
    return [
        {
            "chargerId": 632,
            "userId": 1,
            "theme": "ATMOSPHERE",
            "description": "The views here are amazing",
            "photoUrl": "/img/uploads/IMG_1507.JPG"
        },
        {
            "chargerId": 632,
            "userId": 1,
            "theme": "ATMOSPHERE",
            "description": ('Up for a little detour? Take a drive through '
                            'scenic Skyline Drive, using the Front Royal '
                            'entrance, about 6 miles from the Supercharger'),
            "photoUrl": "/img/uploads/IMG_7666.JPG"
        },
        {
            "chargerId": 632,
            "userId": 1,
            "theme": "FOOD",
            "description": ('If Burger King isn\'t your thing, call Little '
                            'Anthony\'s Pizza, and pick up your order on the '
                            'way to the Supercharger (it\'s right around the '
                            'corner)'),
            "photoUrl":
                ('https://lh3.ggpht.com/p/AF1QipPUpgIgqbOXSziYf_D_iMZhWOwsYa'
                 'rml0TShqKM=s512')

        }
    ]


def get_ratings_default():
    return [{
        'theme': category.strip(),
        'rating': 0
    } for category in os.environ['RATING_TYPES'].split(',')]


def get(event, context):
    dynamodb = boto3.resource('dynamodb')
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
