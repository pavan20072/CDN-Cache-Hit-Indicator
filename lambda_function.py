import json
import os
from datetime import datetime, timezone

import boto3

s3 = boto3.client("s3")

BUCKET_NAME = os.environ["BUCKET_NAME"]
STATUS_KEY = os.environ.get("STATUS_KEY", "status.json")


def lambda_handler(event, context):
    try:
        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)

        action = body.get("action")

        if action == "cache_hit":
            status = "CACHE_HIT"
            message = "Content served from cache successfully (simulated)."
        elif action == "cache_miss":
            status = "CACHE_MISS"
            message = "Content fetched from origin server (simulated)."
        else:
            return response(400, {"error": "Invalid action"})

        result = {
            "status": status,
            "message": message,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "simulation": True
        }

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=STATUS_KEY,
            Body=json.dumps(result).encode("utf-8"),
            ContentType="application/json",
            CacheControl="no-store"
        )

        return response(200, result)

    except Exception as error:
        print("Error:", str(error))
        return response(500, {"error": "Internal server error"})


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }
