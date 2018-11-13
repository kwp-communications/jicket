"""Generate a lambda function and everything required to run it"""

from troposphere import *
from troposphere import awslambda
from troposphere import iam

from awacs import aws as aws_awacs

import os
from typing import List


def getEnvVar(varname, default=None, allowed: List[str] = None):
    """Function to get environment Variables and do some checking along the way"""
    if default is not None:
        var = os.getenv(varname, default)
    else:
        var = os.getenv(varname, None)
        if var is None:
            raise Exception("Required environment variable %s is not set" % varname)

    if allowed is not None and var not in allowed:
        raise Exception("Illegal value for environment variable %s: %s\nAllowed values: %s" % (varname, var, allowed))
    return var


# Variables
# ===========
t = Template("Jicket Deployment")

customername: str = "kwp"  # must be unique across AWS account, as it is used in the lambda function name
if re.search("[^a-z0-9\\-]", customername):
    raise Exception("Illegal characters in customername. Only allowed are 'a-z 0-9 -'")

jicketimaphost = "SETME"
jicketimapport = 993
jicketimapuser = "SETME"
jicketimappass = "SETME"

jicketsmtphost = "SETME"
jicketsmtpport = 587
jicketsmtpuser = jicketimapuser
jicketsmtppass = jicketimappass

jicketticketaddress = "SETME"

jicketjiraurl = "SETME"
jicketjirauser = "SETME"
jicketjirapass = "SETME"
jicketjiraproject = "SETME"

jicketthreadtemplate = "/etc/jicket/threadtemplate.html"

jicketidprefix = "KWP-"  # Prefix used before the ticket id. Should contain a connecting element, e.g. 'KWP-' to produce
# IDs like 'KWP-xxxxxx'

jicketloopmode = "singleshot"


# Execution Role
# ================
lambdaexecutionrole = iam.Role("APILambdaExecutionRole")
lambdaexecutionrole.AssumeRolePolicyDocument = aws_awacs.PolicyDocument(
    Version="2012-10-17",
    Id="S3-Account-Permissions",
    Statement=[
        aws_awacs.Statement(
            Sid="1",
            Effect=aws_awacs.Allow,
            Principal=aws_awacs.Principal("Service", "lambda.amazonaws.com"),
            Action=[aws_awacs.Action("sts", "AssumeRole")]
        )
    ],
)
lambdaexecutionrole.RoleName = "GeolocatorLambdaExecutionRole"
lambdaexecutionrole.ManagedPolicyArns = []
lambdaexecutionrole.Policies = [iam.Policy(
    PolicyName="LambdaExecutionPolicy",
    PolicyDocument=aws_awacs.PolicyDocument(
        Version="2012-10-17",
        Statement=[
        ]
    )
)]

t.add_resource(lambdaexecutionrole)


# Lambda
# ===========
lambdafunc = awslambda.Function("JicketLambda")
lambdafunc.Code = awslambda.Code()
lambdafunc.Code.ZipFile = "# Please upload code :)"
lambdafunc.Description = "Jicket - It really whips the jira's behind!"
lambdafunc.FunctionName = "jicket-" + customername
lambdafunc.Handler = "main.main"
lambdafunc.MemorySize = 128
lambdafunc.Role = GetAtt(lambdaexecutionrole.title, "Arn")
lambdafunc.Runtime = "python3.6"
lambdafunc.Environment = awslambda.Environment(Variables={
    "JICKET_IMAP_HOST": jicketimaphost,
    "JICKET_IMAP_PORT": jicketimapport,
    "JICKET_IMAP_USER": jicketimapuser,
    "JICKET_IMAP_PASS": jicketimappass,

    "JICKET_SMTP_HOST": jicketsmtphost,
    "JICKET_SMTP_PORT": jicketsmtpport,
    "JICKET_SMTP_USER": jicketsmtpuser,
    "JICKET_SMTP_PASS": jicketsmtppass,

    "JICKET_JIRA_URL": jicketjiraurl,
    "JICKET_JIRA_PROJECT": jicketjiraproject,
    "JICKET_JIRA_USER": jicketjirauser,
    "JICKET_JIRA_PASS": jicketjirapass,

    "JICKET_THREAD_TEMPLATE": jicketthreadtemplate,

    "JICKET_TICKET_ADDRESS": jicketticketaddress,

    "JICKET_ID_PREFIX": jicketidprefix,

    "JICKET_LOOPMODE": jicketloopmode,
})

t.add_resource(lambdafunc)


# Print to file
# ===============

t_json = t.to_json()
with open("jicket-lambda.json", "w") as f:
    print(t_json)
    f.write(t_json)
