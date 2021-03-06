import os
from unittest import mock

import boto3
import moto

CHARGERS_TABLE = 'chargers'
TIPS_TABLE = 'tips'


class TestMethodsClass(object):
    status_404 = {
        "statusCode": 404,
        "body": "",
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
        },
    }

    sc_test_data = {
        "id": 632,
        "locationId": "strasburgsupercharger",
        "name": "Strasburg, VA",
        "status": "OPEN",
        "address": {
            "street": "119 Hite Ln",
            "city": "Strasburg",
            "state": "VA",
            "zip": "22657",
            "countryId": 100,
            "country": "USA",
            "regionId": 100,
            "region": "North America"
        },
        "latitude": 39,
        "longitude": -78,
        "dateOpened": "2015-09-02",
        "stallCount": 6,
        "counted": True,
        "elevationMeters": 204,
        "powerKilowatt": 0,
        "solarCanopy": False,
        "battery": False,
        "statusDays": 0,
        "urlDiscuss": True,
    }

    def test_http_put(self):
        from src import charger
        invalid_method = charger.main({'httpMethod': 'PUT'}, None)
        assert invalid_method == self.status_404

    def test_http_post(self):
        from src import charger
        invalid_method = charger.main({'httpMethod': 'POST'}, None)
        assert invalid_method != self.status_404

    @moto.mock_dynamodb2
    @mock.patch.dict(os.environ, {'CHARGERS_TABLE': CHARGERS_TABLE})
    @mock.patch.dict(os.environ, {
        'RATING_TYPES': 'FOOD, KIDS, RESTROOMS, SHOPPING, ATMOSPHERE'
    })
    def test_http_get_all_chargers_invalid(self):
        from src import charger

        event = {
            'httpMethod': 'GET',
            'pathParameters': {
                'id': 'INVALID',
            },
        }

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.create_table(
            TableName=CHARGERS_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        table = dynamodb.Table(CHARGERS_TABLE)
        table.put_item(Item=self.sc_test_data)

        response = charger.main(event, None)
        assert {
            'statusCode': 200,
            'body': '[]',
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true'
            },
        } == response

    @moto.mock_dynamodb2
    @mock.patch.dict(os.environ, {'CHARGERS_TABLE': CHARGERS_TABLE})
    @mock.patch.dict(os.environ, {
        'RATING_TYPES': 'FOOD, KIDS, RESTROOMS, SHOPPING, ATMOSPHERE'
    })
    def test_http_get_all_data(self):
        from src import charger

        event = {
            'httpMethod': 'GET',
            # 'pathParameters': {},
        }

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.create_table(
            TableName=CHARGERS_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        table = dynamodb.Table(CHARGERS_TABLE)
        table.put_item(Item=self.sc_test_data)

        response = charger.main(event, None)
        valid = {
            'statusCode': 200,
            'body': (
                '[{"id": 632.0, "locationId": "strasburgsupercharger", '
                '"name": "Strasburg, VA", "status": "OPEN", "address": {'
                '"street": "119 Hite Ln", "city": "Strasburg", "state": "VA", '
                '"zip": "22657", "countryId": 100.0, "country": "USA", '
                '"regionId": 100.0, "region": "North America"}, "latitude": '
                '39.0, "longitude": -78.0, "dateOpened": "2015-09-02", '
                '"stallCount": 6.0, "counted": '
                'true, "elevationMeters": 204.0, "powerKilowatt": 0.0, '
                '"solarCanopy": false, "battery": false, "statusDays": 0.0, '
                '"urlDiscuss": true}]'),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
            },
        }
        assert valid == response

    @moto.mock_dynamodb2
    @mock.patch.dict(os.environ, {'CHARGERS_TABLE': CHARGERS_TABLE})
    @mock.patch.dict(os.environ, {'TIPS_TABLE': TIPS_TABLE})
    @mock.patch.dict(os.environ, {
        'RATING_TYPES': 'FOOD, KIDS, RESTROOMS, SHOPPING, ATMOSPHERE'
    })
    def test_http_get_specific_charger(self):
        from src import charger

        event = {
            'httpMethod': 'GET',
            'pathParameters': {
                'id': '632',
            },
        }

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.create_table(
            TableName=CHARGERS_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        table = dynamodb.Table(CHARGERS_TABLE)
        table.put_item(Item=self.sc_test_data)

        response = charger.main(event, None)

        valid = {
            'statusCode': 200,
            'body': (
                '{"id": 632.0, "locationId": "strasburgsupercharger", "name": '
                '"Strasburg, VA", "status": "OPEN", "address": {"street": '
                '"119 Hite Ln", "city": "Strasburg", "state": "VA", "zip": '
                '"22657", "countryId": 100.0, "country": "USA", "regionId": '
                '100.0, "region": "North America"}, "latitude": 39.0, '
                '"longitude": -78.0, "dateOpened": "2015-09-02", "stallCount"'
                ': 6.0, "counted": true, "elevationMeters": 204.0, '
                '"powerKilowatt": 0.0, "solarCanopy": false, "battery": '
                'false, "statusDays": 0.0, "urlDiscuss": true, "tips": [], '
                '"ratings": [{"theme": "FOOD", "rating": 0, "count": 0}, {'
                '"theme": "KIDS", "rating": 0, "count": 0}, {"theme": '
                '"RESTROOMS", "rating": 0, "count": 0}, {"theme": "SHOPPING", '
                '"rating": 0, "count": 0}, {"theme": "ATMOSPHERE", '
                '"rating": 0, "count": 0}]}'),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
            },
        }

        assert valid == response

    @moto.mock_dynamodb2
    @mock.patch.dict(os.environ, {'CHARGERS_TABLE': CHARGERS_TABLE})
    @mock.patch.dict(os.environ, {
        'RATING_TYPES': 'FOOD, KIDS, RESTROOMS, SHOPPING, ATMOSPHERE'
    })
    def test_http_get_invalid_charger(self):
        from src import charger

        event = {
            'httpMethod': 'GET',
            'pathParameters': {
                'id': '123',
            },
        }

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

        table = dynamodb.create_table(
            TableName=CHARGERS_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        table = dynamodb.Table(CHARGERS_TABLE)
        table.put_item(Item=self.sc_test_data)

        response = charger.main(event, None)
        print(response)
        valid = {
            'statusCode': 200,
            'body': 'Invalid Charger Id',
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': 'true',
            },
        }
        assert valid == response
