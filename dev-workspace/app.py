import logging
from os import getenv

import aws_cdk as cdk
from common.config import parse_config
from common.constants import CONFIG_DIR
from stack.dev_workspace_stack import DevWorkspaceStack

# Configuration
config = parse_config(CONFIG_DIR)
logging.info("Loaded configuration", config)

# Environment
account = getenv("CDK_DEPLOY_ACCOUNT", getenv("CDK_DEFAULT_ACCOUNT"))
region = getenv("CDK_DEPLOY_REGION", getenv("CDK_DEFAULT_REGION"))
env = cdk.Environment(account=account, region=region)

# App
app = cdk.App()

DevWorkspaceStack(app, "DevWorkspaceStack", config, env=env)

app.synth()
