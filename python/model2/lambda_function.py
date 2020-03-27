import boto3
import pandas as pd

from dataclasses import asdict
from shared_modules.response_model import ModelResponse, RendezvousMessage, BostonRequest, BostonEvent
from typing import List
import json
import time

from shared_modules.forest import score, train

client = boto3.client('sns')
kinesis = boto3.client("kinesis")
s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

bucket = s3_resource.Bucket("bdr-rendezvous-model")

model_name = 'model2'


def handler(event, __):
    records = [BostonEvent(**i) for i in event["Records"]]
    model = train(test_size=0.3, random_state=3, bucket=bucket, model_name=model_name)
    train_score, test_score = score(model, test_size=0.3, random_state=3, model_name=model_name, bucket=bucket)
    messages: List[RendezvousMessage] = [i.body.Message for i in records]


    price = model.predict(pd.DataFrame.from_dict(vals))[0]
    for message in messages:
        print(message)
        now = time.time()
        kinesis.put_record(StreamName=message.data.kinesis_stream,
                           PartitionKey="rendezvous",
                           Data=json.dumps(
                               asdict(ModelResponse(
                                   uuid=message.uuid,
                                   start_time=now,
                                   duration=time.time() - now,
                                   time_after_rendezvous=time.time() - message.rendezvous_time,
                                   model=model_name,
                                   results=json.dumps(
                                       dict(test_score=test_score, train_score=train_score, price=price))))))

        print("DONE")
        return price


if __name__ == "__main__":
    m = {'CRIM': 0.31533,
         'ZN': 0.0,
         'INDUS': 6.2,
         'CHAS': 0.0,
         'NOX': 0.504,
         'RM': 8.266,
         'AGE': 78.3,
         'DIS': 2.8944,
         'RAD': 8.0,
         'TAX': 307.0,
         'PTRATIO': 17.4,
         'B': 385.05,
         'LSTAT': 4.14}
    event_ = {'Records': [{'messageId': 'j',
                           'receiptHandle': 'k',
                           'body': '{\n  "Type" : "f",\n  "MessageId" : "f-6229-5657-8ac9-d8e0a3e6651f",\n  '
                                   '"TopicArn" : "f",\n  "Message" : '
                                   '"{\\"uuid\\": \\"d3e2fc7a-8db3-4b64-aaab-1920809be26f\\", \\"model\\": '
                                   '\\"rendezvous\\", \\"datetime\\": \\"2020-03-26 14:43:27.757108\\", '
                                   '\\"rendezvous_time\\": 1585233807.757103, \\"data\\": {\\"value\\": 100, '
                                   '\\"kinesis_stream\\": \\"rendezvous\\"}}",\n  '
                                   '"Timestamp" : "2020-03-26T14:43:27.936Z",\n  "SignatureVersion" : "1",\n  '
                                   '"Signature" : "x",\n  "SigningCertURL" : "https://sns.eu-west-1.amazonaws.com/Sim'
                                   'pleNotificationService-a86cb10b4e1f29c941702d737128f7b6.pem",\n  "UnsubscribeURL" : "'
                                   'https://sns.eu-west-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:e'
                                   'u-west-1:756285606505:main:4e7f0095-8603-4043-8dfa-49c614b8b7aa"\n}',
                           'attributes': {'k': '1', 'SentTimestamp': 'k',
                                          'SenderId': 'a',
                                          'ApproximateFirstReceiveTimestamp': '1'},
                           'messageAttributes': {},
                           'md5OfBody': 'x',
                           'eventSource': 'aws:sqs',
                           'eventSourceARN': 'arn:aws:sqs:eu-west-1:756285606505:decoy',
                           'awsRegion': 'eu-west-1'}]}
    print(handler(event_, None))
