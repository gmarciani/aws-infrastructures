#!/usr/bin/env python3
import logging
from os import getenv
from os.path import abspath, dirname

import aws_cdk as cdk
from common.config import parse_config
from dev_workspace.dev_workspace_stack import DevWorkspaceStack

config = parse_config(f"{dirname(abspath(__file__))}/config.yaml", f"{dirname(abspath(__file__))}/config.override.yaml")

logging.info("Loaded configuration", config)

app = cdk.App()

account = getenv("CDK_DEPLOY_ACCOUNT", getenv("CDK_DEFAULT_ACCOUNT"))
region = getenv("CDK_DEPLOY_REGION", getenv("CDK_DEFAULT_REGION"))

env = cdk.Environment(account=account, region=region)

DevWorkspaceStack(app, "DevWorkspaceStack", config, env=env)

app.synth()
