Project Structure:
RAGPTCrawler/
├── lambda_function.py
├── RAGPTCrawler.yaml
├── requirements.txt
└── ragptvenv/
    ├── bin/
    ├── include/
    ├── lib/
    └── pyvenv.cfg

AWS CLI
SAM CLI

1. # Create venv
Use the virtual environment and install dependencies:
```
python3 -m venv venv
```

- Activating the Virtual Environment:
```
source venv/bin/activate
```

- Deactivate
```
deactivate
```

2. **Installing and updating Dependencies**: 
- With the virtual environment activated, install the project dependencies with:
```
pip install -r requirements.txt
```
- With the virtual environment activated, update the project dependencies with:
```
python -m pip install --upgrade -r requirements.txt
```


# Deploy the Project (Using SAM CLI):
[One time config] Add aws credential into your local config:
```
vim ~/.aws/credentials

[yi-ragpt]
aws_access_key_id = xxxxxxxxx
aws_secret_access_key = xxxxxxx
```
Build the Lambda function:
```
sam build
```
Deploy the Lambda function. Make sure you config the AWS credential with the right profile name:
```
sam deploy --guided --profile yi-ragpt --config-env default
```

Sample Event:
```
{
  "httpMethod": "FETCH_HTML",
  "queryStringParameters": {
    "url": "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPCD/classification.cfm?id=poc"
  }
}
```

Invoke the Function Locally:
```
sam local invoke -e event.json
```