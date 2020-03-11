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
                                  Data=json.dumps({"uuid": i["uuid"],
                                                   "model": "model1",
                                                   "start_time": now,
                                                   "duration": time.time() - now,
                                                   "results": 'awesome model1'}).encode(),
                                  PartitionKey="rendezvous")

    return resp
