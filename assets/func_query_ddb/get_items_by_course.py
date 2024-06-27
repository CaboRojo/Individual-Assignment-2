import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE'])

def handler(event, context):
    course = event['pathParameters'].get('course')

    if not course:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing path parameter: course'})
        }

    try:
        response = table.query(
            IndexName='Course-index',
            KeyConditionExpression=Key('Course').eq(course)
        )
    except dynamodb.meta.client.exceptions.ValidationException as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'The table does not have the specified index: Course-index'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    if not response['Items']:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'No items found for the given course'})
        }

    return {
        'statusCode': 200,
        'body': json.dumps(response['Items'])
    }
