import boto3
import time

sns = boto3.client('sns')
sqs = boto3.client('sqs')


def handler(_, __):
    publish =  sns.publish(
        TopicArn='arn:aws:sns:eu-west-1:756285606505:main',
        Message='Test at ' + str(time.time())
    )

    queues = sqs.list_queues()

    attrs = {url:sqs.list_queue_tags(QueueUrl=url) for url in queues["QueueUrls"]}

    tags = {url:tag for url, tag in attrs.items() if tag.get("Tags")}
    model_queues = [url for url,tag in tags.items() if tag["Tags"].get("model")=="yes"]
    return publish


if __name__ == "__main__":
    print(handler(None, None))
