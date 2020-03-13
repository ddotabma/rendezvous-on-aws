import boto3
import json
import datetime
import uuid
from model import *
import time

from utils import timer

sns = boto3.client('sns')
kinesis = boto3.client("kinesis")
lambda_client = boto3.client("lambda")
ssm = boto3.client('ssm')

stream_name = 'rendezvous'
model_series = "blog"


@timer
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


@timer
def get_number_from_ssm() -> int:
    value = ssm.get_parameter(Name="number_of_models")["Parameter"]["Value"]
    if value == "0":
        value = service_count()
        ssm.put_parameter(Name="number_of_models", Value=str(value), Type='String', Overwrite=True)
    return int(value)


def handler(event, __):
    id_ = str(uuid.uuid4())
    rendezvous_time = time.time()
    rendezvous_data = json.dumps(dict(uuid=str(id_),
                                      model="rendezvous",
                                      datetime=str(datetime.datetime.utcnow()),
                                      rendezvous_time=rendezvous_time,
                                      data={"value": 100}))
    sns.publish(
        TopicArn='arn:aws:sns:eu-west-1:756285606505:main',
        Message=rendezvous_data
    )
    now = datetime.datetime.utcnow()
    print("Start putting kinesis record after", time.time() - rendezvous_time, "seconds")

    resp = kinesis.put_record(StreamName=stream_name,
                              Data=rendezvous_data,
                              PartitionKey="rendezvous")

    print("Start getting shard iterator kinesis iterator after", time.time() - rendezvous_time, "seconds")

    response_iterator = kinesis.get_shard_iterator(
        StreamName=stream_name,
        ShardId=resp["ShardId"],
        ShardIteratorType="AT_TIMESTAMP",
        Timestamp=now
    )

    print("Done getting shard iterator kinesis iterator after", time.time() - rendezvous_time, "seconds")

    this_call = {}
    services = get_number_from_ssm()
    kinesis_counter = 0
    print("Starting kinesis loop after", time.time() - rendezvous_time, "seconds")

    while (datetime.datetime.utcnow() - now) < datetime.timedelta(seconds=2) and len(this_call) < (services + 1):
        response = kinesis.get_records(
            ShardIterator=response_iterator["ShardIterator"]
        )
        datas = [json.loads(i['Data'].decode()) for i in response['Records']]
        this_call = {i["model"]: i for i in datas if i['uuid'] == id_ and 'model' in i}
        print('cycle ', kinesis_counter, " for kinesis, found", len((this_call)) ,"results")
        kinesis_counter += 1

    if len(this_call) < (services + 1):
        print("not all models returned on time")
    else:
        print("obtained all results after", time.time() - rendezvous_time, "seconds")
    print(this_call)
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(dict(**this_call, **event))
    }


if __name__ == "__main__":
    print(handler(None, None))
