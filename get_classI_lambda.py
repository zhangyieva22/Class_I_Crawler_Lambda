"""
get ClassI device information 
input product_code to get ClassI data
step 1. get product_code from DynamoDB table named Product_code 
step 2. scrapy data from website - classI
step 3. triggle lambda 
step 4. store data into DynamoDB table 
"""


import boto3
from ddb_utils import ddb_fetch_items_by_status, ddb_update_record
from crawler import GetProductCodeData


def lambda_handler(event, context):
    # sourcery skip: use-fstring-for-concatenation
    # For local testing
    # session = boto3.Session(profile_name='yi-ragpt', region_name='us-east-2')
    # dynamodb = session.resource('dynamodb')
    # classI_table = dynamodb.Table("Product_code")
    
    # For AWS Lambda
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    classI_table = dynamodb.Table('Product_code')
    
    items = ddb_fetch_items_by_status(classI_table, status="Not started", desired_count=2)
    
    for item in items:
        product_code = item['product_code']
        ddb_update_record(classI_table, product_code, new_status='Started')
        
        try:
            data = GetProductCodeData(product_code).get_data()
            print("----> data %s \n" % data)
            if data:
                ddb_update_record(classI_table, product_code, new_status='Completed', data=data)
            else:
                ddb_update_record(classI_table, product_code, new_status='No data found')
                
        except Exception as e:
            print('Error processing ' + str(product_code) + ': ' + str(e))
            ddb_update_record(classI_table, product_code, new_status='Failed', data={'error_message': str(e)})


# main function - scrapy classificationI data from fda website using product_code
def main():
    # Mock event and context for local testing
    mock_event = {}
    mock_context = {}

    # Call the lambda handler function
    lambda_handler(mock_event, mock_context)

if __name__ == "__main__":
    main()