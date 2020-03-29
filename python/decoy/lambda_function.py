import boto3
from shared_modules.response_model import ModelResponse, BostonEvent, ModelResult

import time
from dataclasses import asdict

client = boto3.client('sns')
kinesis = boto3.client("kinesis")
s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

model_name = 'decoy'


def handler(sqs_event, __):
    records = [BostonEvent(**i) for i in sqs_event["Records"]]

    for record in records:
        message = record.body.Message
        now = time.time()

        model_response = ModelResponse(  # create instance of standardized response
            uuid=message.uuid,
            start_time=now,
            duration=time.time() - now,
            time_after_rendezvous=time.time() - message.rendezvous_time,
            model=model_name,
            results=asdict(record.body.Message))

        kinesis.put_record(StreamName=message.kinesis_stream,
                           PartitionKey=message.uuid,
                           Data=model_response.json())

    print("DONE")
    return 0  # unused


if __name__ == "__main__":
    body = {"Type": "Notification",
            "MessageId": "some-id",
            "TopicArn": "arn:aws:sns:eu-west-1:756285606505:main",
            "Message": '{"uuid": "268811a2-cb9a-4a23-a66b-b2eea69f0f01", "model": "rendezvous", "datetime": "2020-03-13 14:38:49.752289", "rendezvous_time": 1584110322.4332108, "data": {"value": 100}}',
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
