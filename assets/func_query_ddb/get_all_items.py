import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE'])

def handler(event, context):
    try:
        response = table.scan()
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    if not response['Items']:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'No items found in the database'})
        }

    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'])
    }