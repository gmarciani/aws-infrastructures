#!/usr/bin/env python3
import logging
from os import getenv
from os.path import abspath, dirname

import aws_cdk as cdk
from common.config import parse_config
from dev_workspace.dev_workspace_stack import DevWorkspaceStack

# Configuration
config = parse_config(f"{dirname(abspath(__file__))}/config")
logging.info("Loaded configuration", config)

# Environment
account = getenv("CDK_DEPLOY_ACCOUNT", getenv("CDK_DEFAULT_ACCOUNT"))
region = getenv("CDK_DEPLOY_REGION", getenv("CDK_DEFAULT_REGION"))
env = cdk.Environment(account=account, region=region)

# App
app = cdk.App()

DevWorkspaceStack(app, "DevWorkspaceStack", config, env=env)

app.synth()
