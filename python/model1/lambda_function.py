import boto3
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestRegressor
import json
import time

client = boto3.client('sns')
kinesis = boto3.client("kinesis")


def handler(event, __):
    boston = load_boston()
    boston_df = pd.DataFrame(boston.data, columns=boston.feature_names)
    # print boston_df.info()# add another column that contains the house prices which in scikit learn datasets are considered as target
    boston_df['Price'] = boston.target
    print(boston_df.head(3))
    newX = boston_df.drop('Price', axis=1)
    print(newX[0:3])  # check
    newY = boston_df['Price']  # print type(newY)# pandas core frame
    X_train, X_test, y_train, y_test = train_test_split(newX, newY, test_size=0.3, random_state=3)
    print(len(X_test), len(y_test))
    lr = RandomForestRegressor()

    lr.fit(X_train, y_train)
    train_score = lr.score(X_train, y_train)
    test_score = lr.score(X_test, y_test)
    price = lr.predict(X_test.iloc[:1].values)[0]

    print(event)
    stream_name = 'rendezvous'
    bodies = [json.loads(json.loads(i['body'])['Message']) for i in event['Records']]
    resp = "no records"


    for i in bodies:
        print(i)
        now = time.time()
        resp = kinesis.put_record(StreamName=stream_name,
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
