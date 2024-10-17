import requests
import json

def send_failure_response(webhook_url, message, error_details):
    # Send a failure notification to the frontend with error details
    payload = {
        "status": "FAILURE",
        "message": message,
        "error": error_details
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(webhook_url, data=json.dumps(payload), headers=headers)