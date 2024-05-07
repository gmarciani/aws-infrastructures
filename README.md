<div align="center">
  <img alt="Middy logo" src="https://raw.githubusercontent.com/gmarciani/aws-infrastructures/mainline/docs/images/aws-infrastructures-logo.png"/>
</div>

# AWS Infrastructures
Personal AWS infrastructures defined with CDK.


## Requirements

General:

```
npm install -g npm
npm install -g aws-cdk
python -m pip install --upgrade pip
pre-commit install
```

For specific infrastructure

```
# From within the infrastructure folder (dev-workspace)
pip install -r requirements.txt
```

## Development

To develop a specific infrastructure:

```
# From within the infrastructure folder (eg: dev-workspace)
pip install -r requirements-dev.txt
```

## Usage

### Configuration
Personalize your configuration, adapting the configuration files in `[Infrastructure]/config`
or overriding each original config file with your own:

```
# From within the infrastructure folder (eg: dev-workspace)
cp config/config.yaml [Infrastructure]/config/config.override.yaml
```

### Deployment

Deploy your configuration:

```
# From within the infrastructure folder (eg: dev-workspace)
bash tools/cdk-deploy-to.sh AWS_ACCOUNT_ID AWS_REGION_NAME [--require-approval never]
bash tools/cdk-deploy-everywhere.sh AWS_ACCOUNT_ID [--require-approval never]
```
