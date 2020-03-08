import boto3
import time
import json

sns = boto3.client('sns')
kinesis = boto3.client("kinesis")
import datetime
import uuid
import time

stream_name = 'rendezvous'


def handler(event, __):
    id_ = uuid.uuid1()
    publish = sns.publish(
        TopicArn='arn:aws:sns:eu-west-1:756285606505:main',
        Message=json.dumps(dict(uuid=str(id_),
                                time=str(datetime.datetime.utcnow()),
                                data={"value": 100}))
    )

    now = datetime.datetime.utcnow()
    resp = kinesis.put_record(StreamName=stream_name,
                              Data=json.dumps(dict(rendezvous=str(now),
                                                   uuid=str(id_))).encode(),
                              PartitionKey="rendezvous")

    response_iterator = kinesis.get_shard_iterator(
        StreamName=stream_name,
        ShardId=resp["ShardId"],
        ShardIteratorType="AT_TIMESTAMP",
        Timestamp=now - datetime.timedelta(seconds=10)
    )

    time.sleep(2)
    response = kinesis.get_records(
        ShardIterator=response_iterator["ShardIterator"]
    )

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': [json.loads(i['Data'].decode()) for i in response['Records']]
    }


if __name__ == "__main__":
    print(handler(None, None))
