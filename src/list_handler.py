import json
import boto3

dynamodb = boto3.client("dynamodb")
SUMMARY_TABLE = "UserSummaryTable"


def lambda_handler(event, context):
    """
    GET /list
    → UserSummaryTable の全ユーザを Scan して返す。
    （大量データなら本番では注意。パーティションキー設計やページング等を検討）
    """
    results = []
    paginator = dynamodb.get_paginator('scan')  # from boto3.client('dynamodb') as dynamodb
    for page in paginator.paginate(TableName=SUMMARY_TABLE):
        items = page.get("Items", [])
        for i in items:
            results.append({
                "UserID": i["UserID"]["S"],
                "Name":   i["Name"]["S"]
            })

    return {
        "statusCode": 200,
        "body": json.dumps({"users": results})
    }
