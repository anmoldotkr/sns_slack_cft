import json
import urllib3

# Global variables
WEBHOOK_URL = ""
SLACK_CHANNEL = ""

# Initialize the HTTP client
http = urllib3.PoolManager()

def lambda_handler(event, context):
    # Parse the SNS message
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    # Extract necessary details
    alarm_name = message['AlarmName']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']
    timestamp = message['StateChangeTime']
    sns_region = event['Records'][0]['EventSubscriptionArn'].split(":")[3]
    aws_account_id = event['Records'][0]['EventSubscriptionArn'].split(":")[4]
    alarm_arn = message['AlarmArn']
    metric_value = message['Trigger']['MetricName']
    metric_value_percentage = message['Trigger']['Threshold']
    dimensions = message['Trigger']['Dimensions']
    dimensions_str = ", ".join([f"{dim['name']} = {dim['value']}" for dim in dimensions])


    # Process only ALARM or OK states
    print(new_state)
    if new_state in ["ALARM", "OK"]:
        # Construct AWS Alarm link
        alarm_link = (
            f"https://{sns_region}.console.aws.amazon.com/cloudwatch/home?"
            f"region={sns_region}#alarmsV2:alarm/{alarm_name}"
        )

        # Determine message state and color
        if new_state == "ALARM":
            state_message = f"🚨 *ALERT*: Alarm *{alarm_name}* is now in *ALARM* state.\n\n"
            color = "#FF0000"  # Red for ALARM
        elif new_state == "OK":
            state_message = f"✅ *RECOVERY*: Alarm *{alarm_name}* is now in *OK* state.\n\n"
            color = "#36a64f"  # Green for OK

        # Construct the Slack message payload with attachments for color
        slack_message = {
            'channel': SLACK_CHANNEL,
            'text': (
                f"{state_message}"
                f"*Reason*: {reason}\n"
                f"View Alarm in AWS Console: {alarm_link}"
            ),
            'attachments': [
                {
                    'color': color,
                    'fields': [
                        {'title': "AWS Account", 'value': aws_account_id, 'short': True},
                        {'title': "Alarm ARN", 'value': alarm_arn, 'short': True},
                        {'title': "Alarm Name", 'value': alarm_name, 'short': True},
                        {'title': "State", 'value': new_state, 'short': True},
                        {'title': "Region", 'value': sns_region, 'short': True},
                        {'title': "Metric", 'value': metric_value, 'short': True},
                        {'title': "Threshold", 'value': f"{metric_value_percentage}%", 'short': True},
                        {'title': "Timestamp", 'value': timestamp, 'short': True},
                        {'title': "Resource", 'value': dimensions_str, 'short': True},
                    ]
                }
            ]
        }

        # Send the message to Slack
        encoded_msg = json.dumps(slack_message).encode('utf-8')
        resp = http.request("POST", WEBHOOK_URL, body=encoded_msg, headers={'Content-Type': 'application/json'})

        # Log the response status
        print(f"Message posted to Slack: {resp.status}")
    else:
        # Log and ignore other states
        print(f"Ignored state: {new_state}")
