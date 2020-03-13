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


def train():
    try:
        with BytesIO() as data:
            bucket.download_fileobj("model1.pkl", data)
            data.seek(0)  # move back to the beginning after writing
            lr = pickle.load(data)
        return lr
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

        return lr

def score(model):
    try:
        with BytesIO() as data:
            bucket.download_fileobj("model1.pkl", data)
            data.seek(0)  # move back to the beginning after writing
            lr = pickle.load(data)
        return lr
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

        return lr


def handler(event, __):
    model = train()


    train_score = lr.score(X_train, y_train)
    test_score = lr.score(X_test, y_test)
    price = lr.predict(X_test.iloc[:1].values)[0]

    stream_name = 'rendezvous'
    bodies = [json.loads(json.loads(i['body'])['Message']) for i in event['Records']]

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
    handler(None, None)
