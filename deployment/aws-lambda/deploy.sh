#!/usr/bin/env bash

# Simple script to deploy a jicket instance
# 1.) Install requirements and zip up code
# 2.) Launch cloudformation stack
# 3.) Upload code to stack

STACKNAME=Jicket-KWP-Deployment
FUNCTIONNAME=jicket-kwp

# 1.)
pip install -r Requirements.txt -t lambdacode
zip -r jicket.zip lambdacode/*

# 2.)
python3 jicket_lambda_cloudformationgen.py
aws cloudformation deploy --template-file jicket-lambda.json --stack-name $STACKNAME --no-fail-on-empty-changeset --capabilities CAPABILITY_NAMED_IAM

# 3.)
aws lambda update-function-code --function-name $FUNCTIONNAME --zip-file fileb://jicket.zip