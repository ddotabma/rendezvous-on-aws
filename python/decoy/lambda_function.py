import boto3
import time

client = boto3.client('sns')


def handler(event, __):
    print(event)
    return "OK"

if __name__ == "__main__":
    print(handler(None, None))
