from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__metaclass__ = type
import json


def lambda_handler(event, context):
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
