import boto3
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestRegressor
import json
import time
from io import BytesIO
import pickle

client = boto3.client('sns')
kinesis = boto3.client("kinesis")
s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

bucket = s3_resource.Bucket("bdr-rendezvous-model")

model_name = 'model1'


def train(test_size=0.3, random_state=3):
    try:
        with BytesIO() as data:
            bucket.download_fileobj(f"{model_name}.pkl", data)
            data.seek(0)  # move back to the beginning after writing
            return pickle.load(data)
    except Exception as e:
        print(e)
        boston = load_boston()
        boston_df = pd.DataFrame(boston.data, columns=boston.feature_names)

        boston_df['Price'] = boston.target
        newX = boston_df.drop('Price', axis=1)
        newY = boston_df['Price']
        X_train, X_test, y_train, y_test = train_test_split(newX, newY, test_size=test_size, random_state=random_state)

        lr = RandomForestRegressor()
        lr.fit(X_train, y_train)
        bucket.put_object(Key=f"{model_name}.pkl",
                          Body=pickle.dumps(lr))
        return lr


def score(model, test_size=0.3, random_state=3):
    try:
        with BytesIO() as data:
            bucket.download_fileobj(f"{model_name}_score.json", data)
            data.seek(0)  # move back to the beginning after writing
            scores = json.load(data)
        return scores[0], scores[1]
    except Exception as e:
        print(e)
        boston = load_boston()
        boston_df = pd.DataFrame(boston.data, columns=boston.feature_names)

        boston_df['Price'] = boston.target
        newX = boston_df.drop('Price', axis=1)
        newY = boston_df['Price']
        X_train, X_test, y_train, y_test = train_test_split(newX, newY, test_size=test_size, random_state=random_state)
        train_score, test_score = model.score(X_train, y_train), model.score(X_test, y_test)
        bucket.put_object(Key=f"{model_name}_score.json",
                          Body=json.dumps((train_score, test_score), ensure_ascii=False))

        return model.score(X_train, y_train), model.score(X_test, y_test)


def handler(event, __):
    model = train()
    train_score, test_score = score(model)

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
    price = model.predict(pd.DataFrame.from_dict(vals))[0]
    for i in bodies:
        print(i)
        now = time.time()
        kinesis.put_record(StreamName=stream_name,
                           Data=json.dumps(
                               {"uuid": i["uuid"],
                                "start_time": now,
                                "duration": time.time() - now,
                                "time_after_rendezvous": time.time() - i["rendezvous_time"],
                                "model": model_name,
                                "results": json.dumps(
                                    dict(test_score=test_score, train_score=train_score, price=price))}),
                           PartitionKey="rendezvous")
    print("DONE")

    return price


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
