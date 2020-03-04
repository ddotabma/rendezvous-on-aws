resource "aws_kinesis_stream" "rendezvous" {
  name = "rendezvous"
  shard_count = 1
  shard_level_metrics = [
    "IncomingBytes",
    "OutgoingBytes"
  ]
}