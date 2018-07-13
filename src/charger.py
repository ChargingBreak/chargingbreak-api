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
            "description": "Up for a little detour? Take a drive through scenic Skyline Drive, using the Front Royal entrance, about 6 miles from the Supercharger",
            "photoUrl": "/img/uploads/IMG_7666.JPG"
        },
        {
            "chargerId": 632,
            "userId": 1,
            "theme": "FOOD",
            "description": "If Burger King isn't your thing, call Little Anthony's Pizza, and pick up your order on the way to the Supercharger (it's right around the corner)",
            "photoUrl": "https://lh3.ggpht.com/p/AF1QipPUpgIgqbOXSziYf_D_iMZhWOwsYarml0TShqKM=s512"
        }
    ]


def get_ratings(charger_id):
    return [
        {
            "theme": "FOOD",
            "rating": 3
        },
        {
            "theme": "KIDS",
            "rating": 3
        },
        {
            "theme": "RESTROOMS",
            "rating": 3
        },
        {
            "theme": "SHOPPING",
            "rating": 0
        },
        {
            "theme": "ATMOSPHERE",
            "rating": 5
        }]


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

            # Munge lat/lon, had to un-nest for searching
            data = item['Item']

            # load up tips!
            data['tips'] = get_tips(data['id'])

            # load up ratings
            data['ratings'] = get_ratings(data['id'])

            body = json.dumps(data, cls=de.DecimalEncoder)
        else:
            # Need to work out DynamoDB read limits to pull EVERYTHING
            response = table.scan(os.environ['SUPERCHARGERINFO_TABLE'])
            body = json.dumps(response['Items'], cls=de.DecimalEncoder)
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
