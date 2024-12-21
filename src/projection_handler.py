import json
import boto3

dynamodb = boto3.client("dynamodb")
SUMMARY_TABLE = "UserSummaryTable"
DETAIL_TABLE = "UserDetailTable"


def lambda_handler(event, context):
    """
    EventsTable に書き込まれたイベントを受け取り、
    サマリ用(UserSummaryTable) と 詳細用(UserDetailTable) の両方を更新。
    """
    records = event.get("Records", [])
    for record in records:
        if record["eventName"] == "INSERT":
            new_image = record["dynamodb"]["NewImage"]
            user_id = new_image["AggregateID"]["S"]
            event_type = new_image["EventType"]["S"]
            try:
                payload = json.loads(new_image["Payload"]["S"])
            except json.JSONDecodeError:
                print(f"Failed to parse JSON payload for user {user_id}")
                continue

            if event_type == "USER_CREATED":
                name = payload.get("name", "NoName")
                # Summaries には最小限の項目を保存 (UserID, Name等)
                try:
                    dynamodb.put_item(
                        TableName=SUMMARY_TABLE,
                        Item={
                            "UserID": {"S": user_id},
                            "Name":   {"S": name}
                        }
                    )
                except Exception as e:
                    print(f"Failed to update SUMMARY_TABLE for user {user_id}: {str(e)}")
                # Detail にはより多くの情報を保存
                email = payload.get("email", "noemail@example.com")
                try:
                    dynamodb.put_item(
                        TableName=DETAIL_TABLE,
                        Item={
                            "UserID": {"S": user_id},
                            "Name":   {"S": name},
                            "Email":  {"S": email},
                            "Balance": {"N": "0"}
                        }
                    )
                except Exception as e:
                    print(f"Failed to update DETAIL_TABLE for user {user_id}: {str(e)}")

            elif event_type == "USER_BALANCE":
                # 例: 残高を更新
                delta = payload.get("delta", 0)
                # Summariesは変更しない or 残高表示が必要ならここで更新
                # Detailsだけ更新
                try:
                    dynamodb.update_item(
                        TableName=DETAIL_TABLE,
                        Key={"UserID": {"S": user_id}},
                    UpdateExpression="ADD #B :d",
                    ExpressionAttributeNames={"#B": "Balance"},
                    ExpressionAttributeValues={":d": {"N": str(delta)}}
                )
                except Exception as e:
                    print(f"Failed to update DETAIL_TABLE balance for user {user_id}: {str(e)}")
            # 他のイベントがあれば同様にサマリ・詳細を更新

    return {"statusCode": 200}
