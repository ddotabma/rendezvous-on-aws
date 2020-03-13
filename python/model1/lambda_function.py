import boto3
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestRegressor
import json
import time
from io import BytesIO
import pickle
import numpy as np

client = boto3.client('sns')
kinesis = boto3.client("kinesis")
s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

bucket = s3_resource.Bucket("bdr-rendezvous-model")


def train():
    try:
        with BytesIO() as data:
            bucket.download_fileobj("model1.pkl", data)
            data.seek(0)  # move back to the beginning after writing
            return pickle.load(data)
    except Exception as e:
        print(e)
        boston = load_boston()
        boston_df = pd.DataFrame(boston.data, columns=boston.feature_names)

        boston_df['Price'] = boston.target
        newX = boston_df.drop('Price', axis=1)
        newY = boston_df['Price']
        X_train, X_test, y_train, y_test = train_test_split(newX, newY, test_size=0.3, random_state=3)

        lr = RandomForestRegressor()
        lr.fit(X_train, y_train)
        bucket.put_object(Key="model1.pkl",
                          Body=pickle.dumps(lr))
        return lr


def score(model):
    try:
        with BytesIO() as data:
            bucket.download_fileobj("model1_score.pkl", data)
            data.seek(0)  # move back to the beginning after writing
            scores = pickle.load(data)
        return scores[0], scores[1]
    except Exception as e:
        print(e)
        boston = load_boston()
        boston_df = pd.DataFrame(boston.data, columns=boston.feature_names)

        boston_df['Price'] = boston.target
        newX = boston_df.drop('Price', axis=1)
        newY = boston_df['Price']
        X_train, X_test, y_train, y_test = train_test_split(newX, newY, test_size=0.3, random_state=3)
        train_score, test_score = model.score(X_train, y_train), model.score(X_test, y_test)
        bucket.put_object(Key="model1_score.pkl",
                          Body=json.dumps((train_score, test_score), ensure_ascii=False))

        return model.score(X_train, y_train), model.score(X_test, y_test)


def handler(event, __):
    model = train()
    train_score, test_score = score(model)

    price = model.predict(np.array([[3.1533e-01, 0.0000e+00, 6.2000e+00, 0.0000e+00, 5.0400e-01,
                                     8.2660e+00, 7.8300e+01, 2.8944e+00, 8.0000e+00, 3.0700e+02,
                                     1.7400e+01, 3.8505e+02, 4.1400e+00]]))[0]

    stream_name = 'rendezvous'
    bodies = [json.loads(json.loads(i['body'])['Message']) for i in event['Records']]

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

    for i in bodies:
        print(i)
        now = time.time()
        kinesis.put_record(StreamName=stream_name,
                           Data=json.dumps(
                               {"uuid": i["uuid"],
                                "start_time": i["uuid"],
                                "duration": time.time() - now,
                                "time_after_rendezvous": time.time() - i["rendezvous_time"],
                                "model": "model1",
                                "results": json.dumps({'price': price}).encode()}),
                           PartitionKey="rendezvous")

    return price


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
