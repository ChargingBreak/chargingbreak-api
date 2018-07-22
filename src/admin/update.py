import decimal
import json
import os
import urllib.request

import boto3

DATA_URL = 'https://supercharge.info/service/supercharge/allSites'


def charger_eq(existing, update):
    return all((
        key in existing and existing[key] == update[key]
        for key in update.keys()))


def main(event, context):
    try:
        local_filename, headers = urllib.request.urlretrieve(DATA_URL)
    except Exception as e:
        # some other error happened
        error = str(e)
        return "We had an error: %s" % (error)
    else:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['CHARGERS_TABLE'])

        num_chargers = num_chargers_new = num_chargers_updated = 0
        with open(local_filename) as json_file:
            chargers = json.load(json_file, parse_float=decimal.Decimal)
            for charger in chargers:
                num_chargers += 1
                charger['latitude'] = charger['gps']['latitude']
                charger['longitude'] = charger['gps']['longitude']
                del charger['gps']

                try:
                    existing_charger = table.get_item(
                        Key={'id': int(charger['id'])})['Item']
                except Exception as e:
                    num_chargers_new += 1
                    table.put_item(Item=charger)
                else:
                    if charger_eq(existing_charger, charger):
                        # no need to update
                        continue

                    expressionAttributeNames = dict([
                        ('#%s' % key, key)
                        for key in charger.keys() if key != 'id'])

                    updateExpression = 'set %s' % (', '.join([
                        '#%s = :%s' % (key, key)
                        for key in charger.keys() if key != 'id']))

                    expressionAttributeValues = dict([(
                        ':%s' % key, val)
                        for key, val in charger.items()
                        if key != 'id'])

                    table.update_item(
                        Key={'id': int(charger['id'])},
                        UpdateExpression=updateExpression,
                        ExpressionAttributeNames=expressionAttributeNames,
                        ExpressionAttributeValues=expressionAttributeValues,
                        ReturnValues='NONE',
                    )
                    num_chargers_updated += 1

    return ("We updated %s chargers and created %s chargers for a total "
            "of %s!") % (num_chargers_updated, num_chargers_new, num_chargers)
