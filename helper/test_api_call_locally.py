import json

import requests

with open('config.json', 'rb') as file:
    json_data = json.load(file)

USER_REGISTRATION_API_KEY = json_data['user_registration_api_key']
USER_REGISTER_ENDPOINT = json_data["user_registration_endpoint"]

key = USER_REGISTRATION_API_KEY

horizon_register_user_api_end_point = USER_REGISTER_ENDPOINT

data = {
    "key": key,
    "first_name": "jane",
    "last_name": "doe",
    "email": "jane@horizon.com",
    "company_name": "",
    "business_number": "",
    "mobile_phone": "",
    "industry": "",
    "referral_url": "http://referrer.com"
}

try:
    result = requests.post(url=horizon_register_user_api_end_point, data=data, timeout=15)
    print(result.status_code)
    print(result.content)

except requests.exceptions.Timeout:
    result = None
    diagnostic_message = "Request time out. Check that server IP is white-listed / server has access to the horizon api endpoint."
    print(diagnostic_message)
    request_success = False

except requests.exceptions.TooManyRedirects:
    result = None
    diagnostic_message = "Too many redirects - Check api endpoint url is correct."
    print(diagnostic_message)
    request_success = False

except requests.exceptions.RequestException as e:
    result = None
    diagnostic_message = "Catastrophic error: " + str(e)
    print(diagnostic_message)
    request_success = False


