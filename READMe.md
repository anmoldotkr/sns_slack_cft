
---

## **Documentation for Sending CloudWatch Logs to Slack**

### **Objective**
This setup sends CloudWatch alarm notifications to a Slack channel by using:
1. **Amazon CloudWatch** for monitoring.
2. **Amazon SNS** as the message broker.
3. **AWS Lambda** to format the SNS messages and post them to Slack via a webhook.

### **Prerequisites**
- **AWS Account** with permissions to use CloudWatch, SNS, Lambda, and IAM.
- **Slack Workspace** with a designated channel for alerts and a Slack App with incoming webhook enabled.

### **Architecture Overview**
1. **CloudWatch** triggers an alarm based on set thresholds.
2. The alarm sends a notification to an **SNS topic**.
3. **Lambda** is subscribed to the SNS topic and formats the message to post to **Slack** via an incoming webhook.

---

### **Steps to Configure CloudWatch Alerts to Slack**

#### **1. Create an SNS Topic**

1. Go to the **SNS Console** in AWS.
2. Click **Topics** > **Create topic**.
   - **Type**: Standard.
   - **Name**: Choose a name for your topic, e.g., `cloudwatch-alerts-to-slack`.
3. **Create Topic** and note the **Topic ARN**.

#### **2. Subscribe a Lambda Function to the SNS Topic**

1. In the **SNS Topic** details, click **Create subscription**.
2. **Protocol**: Choose `AWS Lambda`.
3. **Endpoint**: Select the Lambda function you’ll create in the next step.
4. **Create subscription**.

#### **3. Create a Lambda Function**

1. Go to the **Lambda Console** and click **Create function**.
2. **Function name**: Enter a name, e.g., `CloudWatchAlertToSlack`.
3. **Runtime**: Python 3.x (any version supported).
4. **Permissions**: Choose an existing IAM role or create a new one with access to:
   - **AWSLambdaBasicExecutionRole**.
   - **SNS read permissions** (to read from the SNS event).
5. **Function code**: Use the code provided below to format the SNS message and send it to Slack.

#### **4. Add Environment Variables in Lambda**

In the Lambda configuration:
1. Scroll to **Environment variables** and click **Edit**.
2. Add the following variables:
   - **SLACK_WEBHOOK_URL**: Add your Slack webhook URL.
   - **SLACK_CHANNEL**: The Slack channel name (e.g., `#all-testing-alerts`).

#### **5. Set Up Slack Incoming Webhook**

1. Go to [Slack API](https://api.slack.com/apps) and create a **new app** if you don't have one.
2. In your Slack App, enable the **Incoming Webhooks** feature.
3. Set up a new webhook for the desired channel and copy the **Webhook URL**.
4. Paste this URL as the **SLACK_WEBHOOK_URL** environment variable in Lambda.

#### **6. Configure CloudWatch to Use SNS for Alarm Actions**

1. Go to **CloudWatch Console** > **Alarms**.
2. Create a new alarm or edit an existing one.
3. Set the **Alarm actions** to **Send to an SNS topic** and select the SNS topic you created.

#### **7. Lambda Function Code**

Use the following Python code in the Lambda function:

```python
import json
import urllib3
import os

http = urllib3.PoolManager()

def handler(event, context):
    try:
        # Parse SNS message from event
        message = json.loads(event['Records'][0]['Sns']['Message'])
        alarm_name = message.get('AlarmName', 'Unknown Alarm')
        new_state = message.get('NewStateValue', 'Unknown State')
        reason = message.get('NewStateReason', 'No reason provided')

        # Slack webhook URL from environment variable
        webhook_url = os.environ['SLACK_WEBHOOK_URL']
        slack_channel = os.environ['SLACK_CHANNEL']

        # Construct the Slack message payload
        slack_message = {
            'channel': slack_channel,
            'text': f'ALERT: Alarm *{alarm_name}* is now *{new_state}* due to: {reason}'
        }

        # Send the message to Slack
        encoded_msg = json.dumps(slack_message).encode('utf-8')
        resp = http.request("POST", webhook_url, body=encoded_msg, headers={'Content-Type': 'application/json'})
        print(f"Message posted to Slack: {resp.status}")

    except KeyError as e:
        print(f"KeyError: {e}")
        print("The event structure may not match the expected SNS format.")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

---

### **Testing the Setup**

1. **Manually Trigger the Alarm**:
   - You can adjust the threshold temporarily to simulate an alarm condition.

2. **Check Slack**:
   - The Lambda function should post an alert message to your specified Slack channel.

---

### **Notes**

- **Error Handling**: The Lambda code includes error handling to print errors if the SNS message structure isn’t as expected.
- **Permissions**: Ensure that the Lambda’s IAM role has `sns:ReceiveMessage` and `lambda:InvokeFunction` permissions on the SNS topic.
- **Slack Rate Limiting**: If posting frequently, be mindful of Slack’s rate limits on webhooks.
