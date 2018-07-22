import json
from datetime import date, datetime

from src import decimalencoder as de
from src.helpers import get_user


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def get(event, context):

    user_sub = event['pathParameters']['user_sub'] if (
        'pathParameters' in event
        and event['pathParameters']
        and 'user_sub' in event['pathParameters']) else None

    if user_sub:
        attrs = get_user(user_sub)
        if attrs:
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


methods = {
    'GET': get,
}
