import boto3
import json
import datetime
import uuid
from model import *

sns = boto3.client('sns')
kinesis = boto3.client("kinesis")
lambda_client = boto3.client("lambda")

stream_name = 'rendezvous'
model_series = "blog"


def service_count():
    functions = LambdaList(**lambda_client.list_functions())
    services = []
    for function in functions.Functions:
        arn = function.FunctionArn
        tags = lambda_client.list_tags(Resource=arn)["Tags"]
        if "model_series" in tags:
            if tags["model_series"] == model_series:
                services.append(function)

    return len(services)


def handler(event, __):
    id_ = str(uuid.uuid4())
    sns.publish(
        TopicArn='arn:aws:sns:eu-west-1:756285606505:main',
        Message=json.dumps(dict(uuid=str(id_),
                                model="rendezvous",
                                time=str(datetime.datetime.utcnow()),
                                data={"value": 100}))
    )
    now = datetime.datetime.utcnow()

    resp = kinesis.put_record(StreamName=stream_name,
                              Data=json.dumps(dict(rendezvous=str(now),
                                                   uuid=id_)).encode(),
                              PartitionKey="rendezvous")

    response_iterator = kinesis.get_shard_iterator(
        StreamName=stream_name,
        ShardId=resp["ShardId"],
        ShardIteratorType="AT_TIMESTAMP",
        Timestamp=now
    )

    this_call = {}
    services = service_count()
    while (datetime.datetime.utcnow() - now) < datetime.timedelta(seconds=2) and len(this_call) < services:
        response = kinesis.get_records(
            ShardIterator=response_iterator["ShardIterator"]
        )
        datas = [json.loads(i['Data'].decode()) for i in response['Records']]
        this_call = {i["model"]: i for i in datas if i['uuid'] == id_ and 'model' in i}

    if len(this_call) < services:
        print("not all models returned on time")
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': this_call
    }


if __name__ == "__main__":
    print(handler(None, None))
