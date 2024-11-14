import json
import urllib3
import os

http = urllib3.PoolManager()

def lambda_handler(event, context):
    message = json.loads(event['Records'][0]['Sns']['Message'])
    alarm_name = message['AlarmName']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']

    # Add Slack webhook URL
    webhook_url = ""

    # Add the Channel Name
    slack_channel = ""  # Replace with your channel name

    # Construct the Slack message payload
    slack_message = {
        'channel': slack_channel,
        'text': f'ALERT: Alarm *{alarm_name}* is now *{new_state}* due to: {reason}'
    }

    encoded_msg = json.dumps(slack_message).encode('utf-8')
    resp = http.request("POST", webhook_url, body=encoded_msg, headers={'Content-Type': 'application/json'})
    print(f"Message posted to Slack: {resp.status}")