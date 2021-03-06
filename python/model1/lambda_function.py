import boto3
import pandas as pd
from shared_modules.response_model import BostonEvent
from dataclasses import asdict
from shared_modules.forest import score, train, run_model
from typing import List

client = boto3.client('sns')
kinesis = boto3.client("kinesis")
s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

bucket = s3_resource.Bucket("bdr-rendezvous-model")
model_name = 'model1'

model = train(test_size=0.3, random_state=2,
              model_name=model_name, bucket=bucket)

train_score, test_score = score(model, test_size=0.3, random_state=2,
                                model_name=model_name, bucket=bucket)


def predict_prices(records: List[BostonEvent]):
    """Predict prices for all received requests from SQS"""
    return model.predict(pd.DataFrame.from_records([asdict(i.body.Message.data.request) for i in records]))


def handler(sqs_event, __):
    return run_model(model=model,
                     model_name=model_name,
                     test_score=test_score,
                     train_score=train_score,
                     sqs_event=sqs_event)


if __name__ == "__main__":
    import json

    event = {'CRIM': 0.31533,
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
    body = {"Type": "Notification", "MessageId": "5bb7b2c5-841f-588e-a92d-e43279e2292d",
            "TopicArn": "arn:aws:sns:eu-west-1:756285606505:main",
            "Message": json.dumps({"uuid": "144cb9ff-0e08-470c-8c3a-97ad4fbebb6c", "model": "rendezvous",
                                   "datetime": "2020-03-27 13:12:29.854535",
                                   "rendezvous_time": 1585314749.854531, "data":
                                       {"request": event, "kinesis_stream": "rendezvous"}}),
            "Timestamp": "2020-03-27T13:12:29.975Z",
            "SignatureVersion": "1",
            "Signature": "s"}
    records = {'Records': [{'messageId': '969184a4-ba98-4cbe-95b7-0f9c7a6a7948',
                            'receiptHandle': 'ttJ',
                            'body': json.dumps(body),
                            'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1585314750005',
                                           'SenderId': 'AIDAISMY7JYY5F7RTT6AO',
                                           'ApproximateFirstReceiveTimestamp': '1585314750007'},
                            'messageAttributes': {},
                            'md5OfBody': 'd64514f64e6396b0a3d2fc3dba368451', 'eventSource': 'aws:sqs',
                            'eventSourceARN': 'arn:aws:sqs:eu-west-1:756285606505:model2', 'awsRegion': 'eu-west-1'}]}
    # event_ = {'Records': [{'messageId': '969184a4-ba98-4cbe-95b7-0f9c7a6a7948', 'receiptHandle': 'AQEBPe5ijWxdEKxG/P95pJyBKlvxglYGUmSiSudcAgF1ANtKekjhYu7mCjqckgpOOXRAwOq2AkQVlfMCPTjIdsEjxS09WNCDdnf4kqHKx7BagEzRWzsPt3Wl/16wsRIhqxkElepat88j9ssPoD27bsTjFdvpFXFbOMssjr/7KacU5P6WWKR5CKTCuNEwYvz8tSFVgdDQDieBUqYmBvs6Yn3PZ6EQOxeULCZ4G9e8oYG9wAriipLwrGO1C33gKjMBl4/6mXXdFfV6GsRMttJuC4bXHZLimAQuLqcaaIn8ljK+eHYWsnpTyqlWXbn9ucAL1vJHIgOgLQo9QSQ+homh5bt7EhmgwXl4k9OpZPlN7N1JOi5hFyGVnBNFSO4xGr4dm6m+', 'body': '{\n  "Type" : "Notification",\n  "MessageId" : "5bb7b2c5-841f-588e-a92d-e43279e2292d",\n  "TopicArn" : "arn:aws:sns:eu-west-1:756285606505:main",\n  "Message" : "{\\"uuid\\": \\"144cb9ff-0e08-470c-8c3a-97ad4fbebb6c\\", \\"model\\": \\"rendezvous\\", \\"datetime\\": \\"2020-03-27 13:12:29.854535\\", \\"rendezvous_time\\": 1585314749.854531, \\"data\\": {\\"request\\": {\\"CRIM\\": {\\"224\\": 0.31533}, \\"ZN\\": {\\"224\\": 0.0}, \\"INDUS\\": {\\"224\\": 6.2}, \\"CHAS\\": {\\"224\\": 0.0}, \\"NOX\\": {\\"224\\": 0.504}, \\"RM\\": {\\"224\\": 8.266}, \\"AGE\\": {\\"224\\": 78.3}, \\"DIS\\": {\\"224\\": 2.8944}, \\"RAD\\": {\\"224\\": 8.0}, \\"TAX\\": {\\"224\\": 307.0}, \\"PTRATIO\\": {\\"224\\": 17.4}, \\"B\\": {\\"224\\": 385.05}, \\"LSTAT\\": {\\"224\\": 4.14}}, \\"kinesis_stream\\": \\"rendezvous\\"}}
    print(handler(records, None))
