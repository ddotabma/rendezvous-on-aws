import boto3
import time
import json
sns = boto3.client('sns')
kinesis = boto3.client("kinesis")
import datetime

def handler(event, __):
    publish =  sns.publish(
        TopicArn='arn:aws:sns:eu-west-1:756285606505:main',
        Message='Test at ' + str(time.time())
    )
    now = datetime.datetime.utcnow()
    stream_name = 'rendezvous'
    resp = kinesis.put_record(StreamName=stream_name,
                       Data="test " + str(now),
                       PartitionKey="rendezvous")

    shards = kinesis.list_shards(
        StreamName=stream_name
    )

    response_iterator = kinesis.get_shard_iterator(
        StreamName=stream_name,
        ShardId=resp["ShardId"],
        ShardIteratorType= "AT_TIMESTAMP",
        Timestamp=now
    )
    iterator = response_iterator["ShardIterator"]

    response = kinesis.get_records(
        ShardIterator=iterator
    )

    return {
        'statusCode': 200,
        'headers': { 'Content-Type': 'application/json' },
        'body': json.dumps([str(i['Data']) for i in response['Records']])
     }


if __name__ == "__main__":
    print(handler(None, None))
