# -*- coding: utf-8 -*-

# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#    http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

"""Alexa Smart Home Lambda Function Sample Code.

This file demonstrates some key concepts when migrating an existing Smart Home skill Lambda to
v3, including recommendations on how to transfer endpoint/appliance objects, how v2 and vNext
handlers can be used together, and how to validate your v3 responses using the new Validation
Schema.

Note that this example does not deal with user authentication, only uses virtual devices, omits
a lot of implementation and error handling to keep the code simple and focused.
"""

import logging
import time
import json
import uuid
import requests
import os

# Imports for v3 validation
from validation import validate_message

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

UPLIFTED_APPLIANCES = [
  {
    "endpointId": "tv",
    "manufacturerName": "Aled's TV",
    "friendlyName": "TV",
    "description": "Living room tv uplifted by RPi uplift",
    "displayCategories": ["TV"],
    "cookie": {},
    "capabilities":
      [
        {
          "type": "AlexaInterface",
          "interface": "Alexa",
          "version": "3"
        },
        {
          "interface": "Alexa.PowerController",
          "version": "3",
          "type": "AlexaInterface",
          "properties": {
            "supported": [],
            "retrievable": False
          }
        },
        {
          "interface": "Alexa.InputController",
          "version": "3",
          "type": "AlexaInterface",
          "properties": {
            "supported": [],
            "retrievable": False
          }
        }
      ]
  },
  {
    "endpointId": "soundbar",
    "manufacturerName": "Soundbar",
    "friendlyName": "Sound Bar",
    "description": "Soundbar uplifted by RPi uplift",
    "displayCategories": ["SPEAKER"],
    "cookie": {},
    "capabilities":
      [
        {
          "type": "AlexaInterface",
          "interface": "Alexa",
          "version": "3"
        },
        {
          "interface": "Alexa.PowerController",
          "version": "3",
          "type": "AlexaInterface",
          "properties": {
            "supported": [],
            "retrievable": "false"
          }
        },
        {
          "interface": "Alexa.InputController",
          "version": "3",
          "type": "AlexaInterface",
          "properties": {
            "supported": [],
            "retrievable": False
          }
        }
      ]
  }
]


def lambda_handler(request, context):
  """Main Lambda handler.

  Since you can expect both v2 and v3 directives for a period of time during the migration
  and transition of your existing users, this main Lambda handler must be modified to support
  both v2 and v3 requests.
  """

  try:
    logger.info("Directive:")
    logger.info(json.dumps(request, indent=4, sort_keys=True))

    version = get_directive_version(request)

    logger.info("Received v3 directive!")
    if request["directive"]["header"]["name"] == "Discover":
      response = handle_discovery_v3(request)
    else:
      response = handle_non_discovery_v3(request)

    logger.info("Response:")
    logger.info(json.dumps(response, indent=4, sort_keys=True))

    logger.info("Validate v3 response")
    validate_message(request, response)

    return response
  except ValueError as error:
    logger.error(error)
    raise


# v2 handlers
def handle_discovery():
  header = {
    "namespace": "Alexa.ConnectedHome.Discovery",
    "name": "DiscoverAppliancesResponse",
    "payloadVersion": "2",
    "messageId": get_uuid()
  }
  payload = {
    "discoveredAppliances": UPLIFTED_APPLIANCES
  }
  response = {
    "header": header,
    "payload": payload
  }
  return response


def get_utc_timestamp(seconds=None):
  return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))


def get_uuid():
  return str(uuid.uuid4())


# v3 handlers
def handle_discovery_v3(request):
  endpoints = []
  for appliance in UPLIFTED_APPLIANCES:
    endpoints.append(appliance)

  response = {
    "event": {
      "header": {
        "namespace": "Alexa.Discovery",
        "name": "Discover.Response",
        "payloadVersion": "3",
        "messageId": get_uuid()
      },
      "payload": {
        "endpoints": endpoints
      }
    }
  }
  return response


def handle_non_discovery_v3(request):
  request_namespace = request["directive"]["header"]["namespace"]
  request_name = request["directive"]["header"]["name"]
  appliance = request["directive"]["endpoint"]["endpointId"]
  token = request["directive"]["endpoint"]["scope"]["token"]

  formBody = {"secret":os.environ['SECRET']}

  if request_namespace == "Alexa.PowerController":


    if request_namespace == "Alexa.PowerController":
      if request_name == "TurnOn":
        value = "ON"
      else:
        value = "OFF"


    req = requests.post('http://smart.aled-lewis.co.uk:5000/' + appliance + 'on', formBody)

    response = {

      "context": {
        "properties": [{
          "namespace": "Alexa.PowerController",
          "name": "powerState",
          "value": value,
          "timeOfSample": get_utc_timestamp(),
          "uncertaintyInMilliseconds": 500
        }]
      },
      "event": {
        "header": {
          "namespace": "Alexa",
          "name": "Response",
          "payloadVersion": "3",
          "messageId": get_uuid(),
          "correlationToken": request["directive"]["header"]["correlationToken"]
        },
        "endpoint": {
          "scope": {
            "type": "BearerToken",
            "token": token
          },
          "endpointId": request["directive"]["endpoint"]["endpointId"]
        },
        "payload": {}
      }
    }
    return response

  elif request_namespace == "Alexa.InputController":
    payload = request['directive']['payload']['input']
    if (appliance == 'tv'):
      payload = request['directive']['payload']['input']
      logger.info("Payload:"+payload)
      if (payload== 'HDMI 1'):
        requests.post('http://smart.aled-lewis.co.uk:5000/tvinput/hdmi',formBody)
      elif (payload == 'TV'):
        requests.post('http://smart.aled-lewis.co.uk:5000/tvinput/tv',formBody)

    elif (appliance == 'soundbar'):
      requests.post('http://smart.aled-lewis.co.uk:5000/soundbarinput',formBody)


    response = {

      "context": {
        "properties": [{
          "namespace": "Alexa.InputController",
          "name": "input",
          "value": payload,
          "timeOfSample": get_utc_timestamp(),
          "uncertaintyInMilliseconds": 500
        }]
      },
      "event": {
        "header": {
          "namespace": "Alexa",
          "name": "Response",
          "payloadVersion": "3",
          "messageId": get_uuid(),
          "correlationToken": request["directive"]["header"]["correlationToken"]
        },
        "endpoint": {
          "scope": {
            "type": "BearerToken",
            "token": token
          },
          "endpointId": request["directive"]["endpoint"]["endpointId"]
        },
        "payload": {}
      }
    }
    return response

  elif request_namespace == "Alexa.Authorization":
    if request_name == "AcceptGrant":
      response = {
        "event": {
          "header": {
            "namespace": "Alexa.Authorization",
            "name": "AcceptGrant.Response",
            "payloadVersion": "3",
            "messageId": "5f8a426e-01e4-4cc9-8b79-65f8bd0fd8a4"
          },
          "payload": {}
        }
      }
      return response

  # other handlers omitted in this example


# v3 utility functions


def get_directive_version(request):
  try:
    return request["directive"]["header"]["payloadVersion"]
  except:
    try:
      return request["header"]["payloadVersion"]
    except:
      return "-1"
