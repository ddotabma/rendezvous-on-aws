import boto3
import pandas as pd

from dataclasses import asdict
from shared_modules.response_model import ModelResponse, Record, RendezvousMessage
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
    records = [Record(**i) for i in event["Records"]]
    model = train(test_size=0.3, random_state=3, bucket=bucket, model_name=model_name)
    train_score, test_score = score(model, test_size=0.3, random_state=3, model_name=model_name, bucket=bucket)
    stream_name = 'rendezvous'
    messages: List[RendezvousMessage] = [i.body.Message for i in records]

    vals = {'CRIM': {224: 0.31533},
            'ZN': {224: 0.0},
            'INDUS': {224: 6.2},
            'CHAS': {224: 0.0},
            'NOX': {224: 0.504},
            'RM': {224: 8.266},
            'AGE': {224: 78.3},
            'DIS': {224: 2.8944},
            'RAD': {224: 8.0},
            'TAX': {224: 307.0},
            'PTRATIO': {224: 17.4},
            'B': {224: 385.05},
            'LSTAT': {224: 4.14}}
    price = model.predict(pd.DataFrame.from_dict(vals))[0]
    for message in messages:
        print(message)
        now = time.time()
        kinesis.put_record(StreamName=stream_name,
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
    event_ = {'Records': [{'messageId': '001b5b69-2110-4ef9-a62b-19b2f9954f85',
                           'receiptHandle': 'AQEBvBiXZ4XO7HolqCR/VVwwAwfA9NSEpeoo/oKpvxrziqKpUQbr+9EF9Hd18h6KFc9m7wu0Clg'
                                            'da8Yp8eWt/oY2zgRzwZxk5s9pm1W6K/XguPTh5cQTIFpzTuQkb/my1ompKf/O7xxROrB9Ul/OXd'
                                            'xRD7yl8frGSOZXG2WvycxfNihmTExO0RxQYQne1s/y9lHpBseNWnA0gKCulgkGFQyfaqjApeAm3'
                                            'gLmY/O7u39KLlRgoWxbMCR1/mhyI6A+epVTP8Oc+7cE4Wc2kgSf3UPW5M7ftRpkYuk4E+zizryp'
                                            'GcRVMUz8nfGjBiWtpi2eGEj7u1tYUzfpRtMJ4nDsJdfpe3N94cl9hm/ep7kLBg9bbbwAZ2jeLTq'
                                            'vOpBC5b0j5JjK',
                           'body': '{\n  "Type" : "Notification",\n  "MessageId" : "eab18e16-6229-5657-8ac9-d8e0a3e6651f",\n  '
                                   '"TopicArn" : "arn:aws:sns:eu-west-1:756285606505:main",\n  "Message" : '
                                   '"{\\"uuid\\": \\"d3e2fc7a-8db3-4b64-aaab-1920809be26f\\", \\"model\\": '
                                   '\\"rendezvous\\", \\"datetime\\": \\"2020-03-26 14:43:27.757108\\", '
                                   '\\"rendezvous_time\\": 1585233807.757103, \\"data\\": {\\"value\\": 100}}",\n  '
                                   '"Timestamp" : "2020-03-26T14:43:27.936Z",\n  "SignatureVersion" : "1",\n  '
                                   '"Signature" : "hwZLA+RKqeZA0P378JIJF1y8RhIvDcxuFXXSAxy9Vq5jVbLf2FOT1D+9vRq56Ud6llkDc'
                                   'wSZTMZD8yXu3UXsr7fgOU8OZidLNiCWrb6ZpSaIJsz+VDKcxD+2IJQBJMTySqnyfynw904v8//KqcmQabPbNT'
                                   'jAm3/JZlhm8+RcnMlFmqg4ISV3SY1uj09HQkjdFd89eKrWrS9v6Hv+8q6augksbGTKsfwEiuDcIJ1Wh48H3Be'
                                   'KmFZ/qQUz6cuPf6cG91wVl/bpAhR9nxNkOb1ZFeGQhrbWrygS6PvVraYlYl5QYBnJ4hcwFJZOHJpuI+k23+DO'
                                   'dsF0f1+VdIJF3rRqxQ==",\n  "SigningCertURL" : "https://sns.eu-west-1.amazonaws.com/Sim'
                                   'pleNotificationService-a86cb10b4e1f29c941702d737128f7b6.pem",\n  "UnsubscribeURL" : "'
                                   'https://sns.eu-west-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:e'
                                   'u-west-1:756285606505:main:4e7f0095-8603-4043-8dfa-49c614b8b7aa"\n}',
                           'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1585233807974',
                                          'SenderId': 'AIDAISMY7JYY5F7RTT6AO',
                                          'ApproximateFirstReceiveTimestamp': '1585233807978'},
                           'messageAttributes': {},
                           'md5OfBody': 'cde702c2daa9491cde62b9d4143dd5fa',
                           'eventSource': 'aws:sqs',
                           'eventSourceARN': 'arn:aws:sqs:eu-west-1:756285606505:decoy',
                           'awsRegion': 'eu-west-1'}]}
    print(handler(event_, None))
