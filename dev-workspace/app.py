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

env = cdk.Environment(account=getenv("CDK_DEFAULT_ACCOUNT"), region=getenv("CDK_DEFAULT_REGION"))

DevWorkspaceStack(app, "DevWorkspaceStack", config, env=env)

app.synth()
