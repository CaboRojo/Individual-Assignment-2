import json
import os
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE'])

def handler(event, context):
    year = event['pathParameters'].get('year')

    if not year:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing path parameter: year'})
        }

    try:
        response = table.scan(
            FilterExpression=Attr('Year').eq(year)
        )
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    if not response['Items']:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'No items found for the given year'})
        }

    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'])
    }
