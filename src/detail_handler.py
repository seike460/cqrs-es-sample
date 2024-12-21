import json
import boto3

dynamodb = boto3.client("dynamodb")
DETAIL_TABLE = "UserDetailTable"


def lambda_handler(event, context):
    """
    GET /detail?user_id=xxx
    → UserDetailTable から 1ユーザの詳細を取得
    """
    qs = event.get("queryStringParameters", {})
    user_id = qs.get("user_id") if qs else None
    if not user_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing user_id"})
        }

    try:
        response = dynamodb.get_item(
            TableName=DETAIL_TABLE,
            Key={"UserID": {"S": user_id}}
        )
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error retrieving user: {str(e)}"})
        }

    if "Item" not in response:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": f"User {user_id} not found"})
        }

    item = response["Item"]
    detail = {
        "UserID": item["UserID"]["S"],
        "Name":   item["Name"]["S"],
        "Email":  item["Email"]["S"],
        "Balance": int(item["Balance"]["N"])
    }
    return {
        "statusCode": 200,
        "body": json.dumps(detail)
    }
