import boto3
import json
kinesis = boto3.client("kinesis")
from datetime import datetime
import datetime
def handler(event, __):
    now = datetime.datetime.utcnow()
    stream_name = 'rendezvous'
    resp = kinesis.put_record(StreamName=stream_name,
                       Data="XXXXXXXXXXXX", #json.dumps(event),
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
    return "OK"


if __name__ == "__main__":
    print(handler(None, None))
