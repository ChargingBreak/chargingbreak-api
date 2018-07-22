import json
import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from src import decimalencoder as de
from src.helpers import get_user


def post(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['RATINGS_TABLE'])

    postBody = json.loads(event['body'])

    responseBody = "Unknown Error"
    statusCode = 200

    try:
        cid = event['pathParameters']['id'] if (
            'pathParameters' in event
            and event['pathParameters']
            and 'id' in event['pathParameters']) else None
        if cid and cid.isdigit():
            if 'text' in postBody and 'category' in postBody:
                response = table.put_item(
                    Item={
                        'id': str(uuid.uuid4()),
                        'charger_id': int(cid),
                        'user_id': event['requestContext']['authorizer'
                                                           ]['claims']['sub'],
                        'text': postBody['text'],
                        'category': postBody['category']
                    }
                )

                responseBody = json.dumps(response, cls=de.DecimalEncoder)
            else:
                statusCode = 400
                responseBody = json.dumps({'message': 'Invalid parameters'})
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


def get_user_rating_weight(user_id):
    user = get_user(user_id)

    try:
        rating_weight = dict([i.strip().split('=') for i in os.environ[
            'RATING_WEIGHT'].split(',')])
    except Exception as e:
        # just default it
        rating_weight = {
            'USER': '1',
            'VERIFIED': '3',
            'ADMIN': '5',
        }
    try:
        if 'custom:USER_TYPE' in user:
            return rating_weight[user['custom:USER_TYPE']]
    except Exception as e:
        pass

    return 1


def cache(event, context):
    dynamodb = boto3.resource('dynamodb')
    ratings_table = dynamodb.Table(os.environ['RATINGS_TABLE'])
    chargers_table = dynamodb.Table(os.environ['CHARGERS_TABLE'])

    # event = {
    #     'Records': [
    #         {
    #             'eventID': '9b692470fd88d008695841f2a74dec20',
    #             'eventName': 'INSERT',
    #             'eventVersion': '1.1',
    #             'eventSource': 'aws:dynamodb',
    #             'awsRegion': 'us-east-1',
    #             'dynamodb': {
    #                 'ApproximateCreationDateTime': 1532266260.0,
    #                 'Keys': {'id': {'S': '4'}},
    #                 'NewImage': {
    #                     'user_id': {
    #                         'S': '1287461d-b943-4778-8e93-c3e7b847ee80'},
    #                     'rating': {'N': '5'},
    #                     'theme': {'S': 'ATMOSPHERE'},
    #                     'id': {'S': '4'},
    #                     'charger_id': {'N': '129'}
    #                 },
    #                 'SequenceNumber': '10236200000000003079198822',
    #                 'SizeBytes': 85,
    #                 'StreamViewType': 'NEW_AND_OLD_IMAGES'
    #             },
    #             'eventSourceARN': 'arn:aws:dynamodb:us-east-1:343238103616:table/ratings/stream/2018-07-22T13:21:03.940' # noqa: E501
    #         }]}

    try:
        charger_id = event['Records'][0][
            'dynamodb']['NewImage']['charger_id']['N']
    except Exception as e:
        # It didn't work out
        return

    # Q: Why not use some aggregation?
    # A: We want to be able to weight ratings based on user verification status
    #    and can't join tables
    ratings = ratings_table.query(
        KeyConditionExpression=Key('charger_id').eq(int(charger_id)),
        IndexName='charger_id-index',
        ProjectionExpression='theme, rating, user_id'
    )

    # just be safe
    if not ('Count' in ratings and ratings['Count'] > 0):
        return

    users = {}
    compiled_ratings = {}
    for category in os.environ['RATING_TYPES'].split(','):
        category = category.strip()
        compiled_ratings[category] = {
            'count': 0,
            'rating': 0,
        }

    for rating in ratings['Items']:
        category = rating['theme']
        if rating['user_id'] not in users:
            users[rating['user_id']] = get_user_rating_weight(
                rating['user_id'])
        user_rating_weight = users[rating['user_id']]
        compiled_ratings[category]['count'] += user_rating_weight
        for r in range(0, user_rating_weight):
            compiled_ratings[category]['rating'] += rating['rating']

    avg_ratings = [{'theme': theme,
                    'rating': round(r['rating'] / r['count']
                                    ) if r['count'] > 0 else 0}
                   for theme, r in compiled_ratings.items()]

    chargers_table.update_item(
        Key={
            'id': int(charger_id),
        },
        UpdateExpression='set ratings = :ratings',
        ExpressionAttributeValues={
            ':ratings': avg_ratings,
        },
        ReturnValues='NONE',
    )
