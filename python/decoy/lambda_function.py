import boto3
import json
kinesis = boto3.client("kinesis")
from datetime import datetime

def handler(event, __):
    resp = kinesis.put_record(StreamName='rendezvous',
                       Data="XXXXXXXXXXXX", #json.dumps(event),
                       PartitionKey="test")

    shards = kinesis.list_shards(
        StreamName='rendezvous'
    )
    response_iterator = kinesis.get_shard_iterator(
        StreamName='rendezvous',
        ShardId='shardId-000000000000',
        ShardIteratorType= 'TRIM_HORIZON',
        # StartingSequenceNumber='string',
        # Timestamp=datetime(2015, 1, 1)
    )
    response = kinesis.get_records(
        ShardIterator=response_iterator["ShardIterator"]
    )

    print(response)
    return "OK"


if __name__ == "__main__":
    print(handler(None, None))
