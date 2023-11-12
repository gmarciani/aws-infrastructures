<div align="center">
  <img alt="Middy logo" src="https://raw.githubusercontent.com/gmarciani/aws-infrastructures/mainline/docs/images/aws-infrastructures-logo.png"/>
</div>

# AWS Infrastructures
Personal AWS infrastructures defined with CDK.


## Requirements

General:

```
npm install -g aws-cdk
python -m pip install --upgrade pip
pre-commit install
```

For specific infrastructure

```
pip install -r [Infrastructure]/requirements.txt
```

## Development

To develop a specific infrastructure:

```
pip install -r [Infrastructure]/requirements-dev.txt
```

## Usage

### Configuration
Personalize your configuration, adapting the configuration files in `[Infrastructure]/config`
or overriding each original config file with your own:

```
cp [Infrastructure]/config/config.yaml cp [Infrastructure]/config/config.override.yaml
```

### Deployment

Deploy your configuration:

```
[Infrastructure]/tools/cdk-deploy-to.sh AWS_ACCOUNT_ID AWS_REGION_NAME [--require-approval never]
[Infrastructure]/tools/cdk-deploy-everywhere.sh AWS_ACCOUNT_ID [--require-approval never]
```
