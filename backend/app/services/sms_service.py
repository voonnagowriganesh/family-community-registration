import os
import requests

MSG91_AUTH_KEY = os.getenv("MSG91_AUTH_KEY")
MSG91_TEMPLATE_ID = os.getenv("MSG91_TEMPLATE_ID")

def send_otp_sms(mobile_number: str, otp: str):
    url = "https://control.msg91.com/api/v5/flow/"

    payload = {
        "flow_id": MSG91_TEMPLATE_ID,
        "recipients": [
            {
                "mobiles": f"91{mobile_number}",
                "otp": otp
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "authkey": MSG91_AUTH_KEY
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)

    print("MSG91 STATUS:", response.status_code)
    print("MSG91 RESPONSE:", response.text)

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()
