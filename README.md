# AWS Infrastructures
Personal AWS infrastructures defined with CDK.


## Requirements
```
npm install -g aws-cdk
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Development
```
pip install pre-commit
pre-commit install
```

## Usage

```
[Infrastructure]/tools/cdk-deploy-to.sh AWS_ACCOUNT_ID AWS_REGION_NAME [--require-approval never]
[Infrastructure]/tools/cdk-deploy-everywhere.sh AWS_ACCOUNT_ID [--require-approval never]
```
