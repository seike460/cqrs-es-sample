import json
import time
import uuid
import boto3
import os

dynamodb = boto3.client("dynamodb")
EVENTS_TABLE = os.environ.get("EVENTS_TABLE", "EventsTable")  # Get from environment variable

def lambda_handler(event, context):
    """
    /command に POST されたデータをイベントとして EventsTable に書き込む。
    例: {"user_id": "user-001", "event_type": "USER_CREATED", "payload": {"name": "Alice","email":"..."}}
    """
    try:
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_id", "unknown-id")
        event_type = body.get("event_type", "UNKNOWN_EVENT")
        payload = body.get("payload", {})

        # Sequence を uuid などで発行
        sequence = str(uuid.uuid4())

        # PutItem
        try:
            dynamodb.put_item(
                TableName=EVENTS_TABLE,
                Item={
                    "AggregateID": {"S": user_id},
                    "Sequence":    {"S": sequence},
                    "EventType":   {"S": event_type},
                    "Payload":     {"S": json.dumps(payload)},
                    "Timestamp":   {"S": str(time.time())}
                }
            )
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"Failed to store event: {str(e)}"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Event stored",
                "aggregate_id": user_id,
                "event_type": event_type,
                "sequence": sequence
            })
        }
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }
