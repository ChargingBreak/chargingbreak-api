import json
import os
from datetime import date, datetime

import boto3
from src import decimalencoder as de


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def get(event, context):
    user_pool_arn = os.environ['USER_POOL_ARN']
    user_pool_id = user_pool_arn.split(':')[5].split('/')[1]

    user_sub = event['pathParameters']['user_sub'] if (
        'pathParameters' in event
        and event['pathParameters']
        and 'user_sub' in event['pathParameters']) else None

    if user_sub:
        client = boto3.client('cognito-idp')
        users = client.list_users(
            UserPoolId=user_pool_id,
            Filter="sub = '%s'" % user_sub,
        )

        if users and 'Users' in users and len(users['Users']) > 0:
            user_raw = users['Users'][0]

            # Attributes is an array of dict, lets simplify
            attrs = {a['Name']: a['Value'] for a in user_raw['Attributes']}
            user_info = {
                'name': attrs['name'],
                'photoUrl': attrs['picture'],
                'sub': attrs['sub'],
            }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    user_info,
                    cls=de.DecimalEncoder,
                    default=json_serial),
                "headers": {
                    # TODO: MPN: need to set this for real before live
                    # useful to have * for now for local dev
                    # 'https://chargingbreak.com'
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true',
                },
            }

    # all else fails, give a 404
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


methods = {
    'GET': get,
}


def main(event, context):
    if 'httpMethod' in event:
        return methods[event['httpMethod']](event, context)

    return {
        "statusCode": 404,
        "body": "{}",
        "headers": {
            # TODO: MPN: need to set this for real before live
            # useful to have * for now for local dev
            # 'https://chargingbreak.com'
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
        },
    }
