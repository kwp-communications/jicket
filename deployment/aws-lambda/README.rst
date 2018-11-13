Deploying Jicket on AWS Lambda
===============================

AWS Lambda allows you to run code without having to manage a server to run the code on. Jicket can be run on Lambda in
singleshot mode.


How-To
--------

1. Edit all variables in `jicket_lambda_cloudformationgen.py` to desired values. Check documentation for information about which values to set.

2. Edit the two variables in `deploy.sh` to reflect the information set in the python script

3. Run `deploy.sh` from within this folder. Make sure you have correct AWS credentials set. If necessary set the correct profile in `deploy.sh`.