import boto3
from datetime import datetime 

def ddb_update_status_to_not_started(session, table_name):
    # Initialize a DynamoDB resource
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    # Scan the table for items where status is not "Not started"
    scanning = True
    start_key = None
    while scanning:
        scan_kwargs = {
            'FilterExpression': "#st <> :status",
            'ExpressionAttributeNames': {'#st': 'status'},
            'ExpressionAttributeValues': {":status": "Not started"}
        }
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key
        
        response = table.scan(**scan_kwargs)
        
        # Update each item where status is not "Not started"
        for item in response['Items']:
            print(f"Updating product_code {item['product_code']}...")
            update_response = table.update_item(
                Key={'product_code': item['product_code']},
                UpdateExpression="SET #st = :newstatus",
                ExpressionAttributeNames={"#st": "status"},
                ExpressionAttributeValues={":newstatus": "Not started"},
                ReturnValues="UPDATED_NEW"
            )
            print(f"Update response: {update_response['Attributes']}")

        # Handle pagination if there are more items to scan
        start_key = response.get('LastEvaluatedKey', None)
        scanning = start_key is not None

def ddb_get_item_count(session, table_name):
    # Initialize a DynamoDB client using this session
    dynamodb = session.client('dynamodb')
    
    # Get the table description
    response = dynamodb.describe_table(TableName=table_name)
    
    # Extract the item count
    item_count = response['Table']['ItemCount']
    print(f"Item count in table {table_name}: {item_count}")
    return item_count

def ddb_reset_data_if_updated_exists(session, table_name):
    # Initialize a DynamoDB resource
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # Scan for items where 'update_at' is not empty
    scan_response = table.scan(
        FilterExpression="attribute_exists(update_at)"
    )
    items = scan_response.get('Items', [])

    # Process each item that has an 'update_at' set
    for item in items:
        product_code = item['product_code']
        try:
            # Reset 'create_at', 'data', and 'update_at'
            update_response = table.update_item(
                Key={'product_code': product_code},
                UpdateExpression='SET #create_at = :empty, #data = :empty, #update_at = :empty',
                ExpressionAttributeNames={
                    '#create_at': 'create_at',
                    '#data': 'data',
                    '#update_at': 'update_at'
                },
                ExpressionAttributeValues={
                    ':empty': None  # Setting to None to represent empty in DynamoDB
                }
            )
            print(f"Data reset for product_code {product_code}.")
        except Exception as e:
            print(f"Error resetting data for product_code {product_code}: {e}")

def ddb_fetch_items_by_status(table, status="Not started", desired_count=20):
    
    query_kwargs = {
        "IndexName": "status-index",
        "KeyConditionExpression": "#status = :statusVal",
        "ExpressionAttributeNames": {"#status": "status"},
        "ExpressionAttributeValues": {":statusVal": status},
        "Limit": desired_count
    }
    response = table.query(**query_kwargs)
    items = response.get('Items', [])
    print(items)
    return items


def ddb_update_status(table, product_code, new_status, data=None):
    # Prepare the update expression to set 'update_at' and conditionally set 'create_at'
    update_expression = 'SET #status = :new_status, #update_at = :update_at,  #create_at = if_not_exists(#create_at, :create_at)'
    expression_attribute_names = {
        '#status': 'status',
        '#update_at': 'update_at',
        '#create_at': 'create_at'
    }
    expression_attribute_values = {
        ':new_status': new_status,
        ':update_at': datetime.now().isoformat(),
        ':create_at': datetime.now().isoformat()
    }

    # Conditionally add data field if it's provided
    if data:
        update_expression += ', #data = :data'
        expression_attribute_names['#data'] = 'data'
        expression_attribute_values[':data'] = data

    # Execute the update item operation
    try:
        update_response = table.update_item(
            Key={'product_code': product_code},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
        print(f"Update response: {update_response}")
    except Exception as e:
        print(f"Failed to update item: {e}")

def main():
    table_name = 'Product_code'
    session = boto3.Session(profile_name='yi-ragpt', region_name='us-east-2')
    dynamodb_resource = session.resource('dynamodb')     
    table = dynamodb_resource.Table(table_name)
    # update_status_to_not_started(session, table_name)
    # reset_data_if_updated_exists(session, table_name)
    # get_item_count(session, table_name)  #6904
    ddb_fetch_items_by_status(table)
 
if __name__ == "__main__":
    main()
