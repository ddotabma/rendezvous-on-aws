import boto3
import time

client = boto3.client('sns')


def handler(_, __):
    return client.publish(
        TopicArn='arn:aws:sns:eu-west-1:756285606505:main',
        Message='Test at ' + str(time.time())
    )


if __name__ == "__main__":
    print(handler(None, None))
