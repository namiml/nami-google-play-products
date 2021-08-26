#!/usr/bin/python3

import sys
import getopt
import json

from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
from googleapiclient import discovery, errors

from pyasn1.error import SubstrateUnderrunError

STATUS_CODE_EMOJI = {}
STATUS_CODE_EMOJI[404] = "❓"
STATUS_CODE_EMOJI[401] = "🔐"
STATUS_CODE_EMOJI[400] = "💣"
STATUS_CODE_EMOJI[000] = "🚨"

def fetch_iap_products(service_credentials_path, package_name):
    try:
        credentials_response = service_account.Credentials.from_service_account_file(
    service_credentials_path)
    
    except ValueError as error:
        print(f"{STATUS_CODE_EMOJI[401]} {error}")
        return
    except DefaultCredentialsError as error:
        print(f"{STATUS_CODE_EMOJI[401]} {error}")
        return
    except SubstrateUnderrunError as error:
        print(f"{STATUS_CODE_EMOJI[401]} The service credentials are malformed")
        return 

    if type(credentials_response) is service_account.Credentials:
        credentials = credentials_response
    else:
        print(f"{STATUS_CODE_EMOJI[401]} Unknown error with service account credentials.")
        return

    service = discovery.build(
        "androidpublisher", "v3", credentials=credentials, cache_discovery=False
    )

    
    request = (
        service.inappproducts()
        .list(packageName=package_name)
    )



    try:
        response = request.execute()
    except errors.HttpError as error:
        error_content = json.loads(error.content)
        if "error" in error_content:
            error = error_content["error"]

            if "code" in error:
                status_code = error["code"]
            else:
                status_code = 000

            if "message" in error:
                message = error["message"]
            else:
                message = "Unknown error"

            # If this message is Invalid Value, it may mean a subscription token sent to the onetime purchase API
            # or a onetime purchase token sent to the subscription API
            print(f"{STATUS_CODE_EMOJI[status_code]} {message}")
    else:
        print(response)


if __name__ == "__main__":
    help_message = "google_token_validator.py /path/to/service_credentials.json [package_name] <OPTIONAL: --quiet>"

    if len(sys.argv) < 3:
        print(help_message)
        sys.exit(2)

    service_credentials = sys.argv[1] 
    package_name = sys.argv[2]

    fetch_iap_products(service_credentials, package_name)
