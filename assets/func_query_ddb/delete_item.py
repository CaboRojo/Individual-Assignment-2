import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE'])

def handler(event, context):
    try:
        item_id = event['pathParameters'].get('id')
        course = event['queryStringParameters'].get('course')
        
        if not item_id or not course:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required parameters: id and/or course'})
            }
        
        try:
            response = table.delete_item(
                Key={'ItemId': item_id, 'Course': course},
                ReturnValues='ALL_OLD'
            )
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'An error occurred while deleting the item: {}'.format(str(e))})
            }
        
        if 'Attributes' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Item not found'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Item deleted successfully'})
        }
    
    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Bad request: missing {}'.format(str(e))})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'An unknown error occurred: {}'.format(str(e))})
        }