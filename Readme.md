# Class_I_Crawler_Lambda
## Prerequisites
- AWS CLI
- SAM CLI

## Setup

### 1. Create Virtual Environment
Use the virtual environment and install dependencies:
```bash
python3 -m venv venv
```

### 2. Activate the Virtual Environment
```bash
source venv/bin/activate
```

### 3. Deactivate the Virtual Environment
```bash
deactivate
```

### 4. Install and Update Dependencies
With the virtual environment activated, install the project dependencies:
```bash
pip install -r requirements.txt
```

To update the project dependencies:
```bash
python -m pip install --upgrade -r requirements.txt
```

## Deploy the Project (Using SAM CLI)

### 1. Configure AWS Credentials
Add AWS credentials to your local config (one-time configuration):
```bash
vim ~/.aws/credentials
```

Add the following lines:
```
[yi-ragpt]
aws_access_key_id = xxxxxxxxx
aws_secret_access_key = xxxxxxx
```

### 2. Build the Lambda Function
```bash
sam build
```

### 3. Deploy the Lambda Function
Make sure you configure the AWS credentials with the right profile name:
```bash
sam deploy --guided --profile yi-ragpt --config-env default
```

## Sample Event
```json
{
  "httpMethod": "FETCH_HTML",
  "queryStringParameters": {
    "url": "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPCD/classification.cfm?id=poc"
  }
}
```

## Invoke the Function Locally
```bash
sam local invoke -e event.json
```

# Check tables
```
aws dynamodb list-tables --profile yi-ragpt --region us-east-2
```

