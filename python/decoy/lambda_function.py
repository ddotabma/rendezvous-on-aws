import boto3
import json
import datetime

kinesis = boto3.client("kinesis")


def handler(event, __):
    print(event)
    stream_name = 'rendezvous'
    bodies = [json.loads(json.loads(i['body'])['Message']) for i in event['Records']]
    resp = "no records"
    for i in bodies:
        print(i)
        resp = kinesis.put_record(StreamName=stream_name,
                                  Data=json.dumps({**i,
                                                   "mode": "decoy",
                                                   "results": 'awesome'}).encode(),
                                  PartitionKey="rendezvous")

    return resp


if __name__ == "__main__":
    body = {"Type": "Notification",
            "MessageId": "some-id",
            "TopicArn": "arn:aws:sns:eu-west-1:756285606505:main",
            "Message": '{"foo": "bar"}',
            "Timestamp": "2020-03-08T15:06:23.149Z",
            "SignatureVersion": "1",
            "Signature": 'signature',
            "SigningCertURL": "some-pemk",
            "UnsubscribeURL": "some-url"}
    event = {'Records': [{'messageId': '7ee38a85-2033-4c1b-8cc8-13d2d2fd0820',
                          'receiptHandle': 'string',
                          'body': json.dumps(body),
                          'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1583679983189',
                                         'SenderId': 'AIDAISMY7JYY5F7RTT6AO',
                                         'ApproximateFirstReceiveTimestamp': '1583679983258'},
                          'messageAttributes': {},
                          'md5OfBody': '371d062ddfe2be3da7c44b4a1126e524', 'eventSource': 'aws:sqs',
                          'eventSourceARN': 'arn:aws:sqs:eu-west-1:756285606505:decoy', 'awsRegion': 'eu-west-1'}]}
    print(handler(event, None))
