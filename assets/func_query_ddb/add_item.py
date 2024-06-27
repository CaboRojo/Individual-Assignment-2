import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE'])
counter_table = dynamodb.Table(os.environ['COUNTER_TABLE'])

def handler(event, context):
    try:
        body = json.loads(event['body'])
    except (json.JSONDecodeError, TypeError):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request payload'})
        }

    required_fields = ['name', 'course', 'year']
    if not all(field in body for field in required_fields):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing required fields: {required_fields}'})
        }

    # Increment the counter
    response = counter_table.update_item(
        Key={'CounterName': 'ItemIdCounter'},
        UpdateExpression='SET CounterValue = if_not_exists(CounterValue, :start) + :inc',
        ExpressionAttributeValues={':inc': 1, ':start': 0},
        ReturnValues='UPDATED_NEW'
    )
    item_id = str(response['Attributes']['CounterValue'])

    item = {
        'ItemId': item_id,
        'Name': body['name'],
        'Course': body['course'],
        'Year': body['year']
    }
    
    # Include additional fields if present
    additional_fields = {k: v for k, v in body.items() if k not in required_fields}
    item.update(additional_fields)

    try:
        table.put_item(Item=item)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    
    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Item added successfully', 'item': item})
    }
