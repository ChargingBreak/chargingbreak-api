import os

import boto3


def get_user(user_sub):
    user_pool_arn = os.environ['USER_POOL_ARN']
    user_pool_id = user_pool_arn.split(':')[5].split('/')[1]

    client = boto3.client('cognito-idp')
    users = client.list_users(
        UserPoolId=user_pool_id,
        Filter="sub = '%s'" % user_sub,
    )

    if not(users and 'Users' in users and len(users['Users']) > 0):
        return None

    user_raw = users['Users'][0]

    # Attributes is an array of dict, lets simplify
    attrs = {a['Name']: a['Value'] for a in user_raw['Attributes']}
    return attrs
