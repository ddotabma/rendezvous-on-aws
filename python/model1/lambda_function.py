import boto3
import time
import json

client = boto3.client('sns')
kinesis = boto3.client("kinesis")


def handler(event, __):
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
                                       "results": 'awesome model1'}).encode(),
                                  PartitionKey="rendezvous")

    return resp
