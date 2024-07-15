"""
get ClassI device information 
input product_code to get ClassI data
step 1. get product_code from DynamoDB table named Product_code 
step 2. scrapy data from website - classI
step 3. triggle lambda 
step 4. store data into DynamoDB table 
"""

import requests
from scrapy import Selector as sel
from datetime import datetime 
import boto3
from botocore.exceptions import NoCredentialsError



dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
classI_table = dynamodb.Table('Product_code')


def lambda_handler(event, context):
    # Scan DynamoDB to get 10 records with the status "Not started"
    scan_response = classI_table.scan(
        FilterExpression='status = :status',
        ExpressionAttributeNames={
            '#status': 'status'
        },
        ExpressionAttributeValues={
            ':status': 'Not started'
        },
        Limit=10
    )
    
    items = scan_response.get('Items', [])
    
    
    for item in items:
        product_code = item['product_code']
        update_status(product_code, 'in progress')
        
        try:
            dataGet = getData(product_code)
            data = dataGet.get_classI_data()
            if data:
                update_status(product_code, 'Completed', data)
            else:
                update_status(product_code, 'No data found')
                
        except Exception as e:
            print(f'Error processing: {product_code}: {e}')
            update_status(product_code, 'fail', {'error_message': str(e)})

def update_status(product_code, new_status, data=None):
    update_expression = 'SET status = :new_status, update_at = :update_at'
    expression_attribute_names = {'#status': 'status'}
    expression_attribute_values = {
        ':new_status': new_status,
        ':update_at': datetime.now().isoformat()
    }
    
    if data:
        update_expression += ', data = :data, create_at = if_not_exists(create_at, :create_at)'
        expression_attribute_names['#data'] = 'data'
        expression_attribute_values[':data'] = data
        expression_attribute_values[':create_at'] = datetime.now().isoformat()
    
    classI_table.update_item(
        Key={'product_code': product_code},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values
    )

# main function - scrapy classificationI data from fda website using product_code
class getData:
    def __init__(self, product_code):
        self.product_code = product_code
        self.url = self.generate_url()
        self.selector = self.fetch_html()

    def generate_url(self):
        if isinstance(self.product_code, str) and self.product_code.isalpha():
            return f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPCD/classification.cfm?id={self.product_code}"
        raise ValueError(f"Invalid product code: {self.product_code}")

    def fetch_html(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return sel(text=response.content)
        except requests.RequestException as e:
            print(f"Error fetching URL {self.url}: {e}")
            raise

    def extract_with_default(selector, query, default='N/A'):
        return selector.xpath(query).extract_first(default=default)
    
    # ClassI data extraction - 13 fields
    def get_classI_data(self):
        return {
            'device': self.extract_with_default( "//tr/th[text()='Device']/following-sibling::td[1]/text()").title(),
            'regulation_description': self.extract_with_default( "//tr/th[text()='Regulation Description']/following-sibling::td[1]/text()"),
            'regulation_medical_specialty': self.extract_with_default( "//tr/th[text()='Regulation Medical Specialty']/following-sibling::td[1]/text()"),
            'review_panel': self.extract_with_default( "//tr/th[text()='Review Panel']/following-sibling::td[1]/text()").strip(),
            'product_code': self.extract_with_default( "//tr/th[text()='Product Code']/following-sibling::td[1]/text()"),
            'submission_type': self.extract_with_default( "//tr/th[text()='Submission Type']/following-sibling::td[1]/text()").strip(),
            'regulation_number': self.extract_with_default( "//tr/th[text()='Regulation Number']/following-sibling::td[1]/a/text()"),
            'device_class': self.extract_with_default( "//tr/th[text()='Device Class']/following-sibling::td[1]/text()").strip(),
            'gmp_exempt': self.extract_with_default( "//tr/th[text()='GMP Exempt?']/following-sibling::td[1]/text()").strip(),
            'summary_malfunction_reporting': self.extract_with_default( "//tr/th[text()='Reporting']/following-sibling::td[1]/text()"),
            'implanted_device': self.extract_with_default( "//tr/th[contains(text(), 'Implanted Device?')]/following-sibling::td[1]/text()").strip(),
            'life_sustain_support_device': self.extract_with_default( "//tr/th[contains(text(), 'Life-Sustain/Support Device?')]/following-sibling::td[1]/text()").strip(),
            'url': self.url
        }
    

