import decimal
import json
import os
import urllib.request

import boto3

DATA_URL = 'https://supercharge.info/service/supercharge/allSites'


def main(event, context):
    try:
        local_filename, headers = urllib.request.urlretrieve(DATA_URL)
    except Exception as e:
        # some other error happened
        error = str(e)
    else:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['SUPERCHARGERINFO_TABLE'])

        num_chargers = 0
        with table.batch_writer() as batch:
            with open(local_filename) as json_file:
                chargers = json.load(json_file, parse_float=decimal.Decimal)
                for charger in chargers:
                    charger['latitude'] = charger['gps']['latitude']
                    charger['longitude'] = charger['gps']['longitude']
                    del charger['gps']

                    batch.put_item(Item=charger)
                    num_chargers = num_chargers + 1

    return "We loaded up %s chargers!" % (num_chargers)
