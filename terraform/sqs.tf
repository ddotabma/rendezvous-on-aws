resource "aws_sqs_queue" "model1" {
  name = "model1"
  delay_seconds = 0
  max_message_size = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10

}

resource "aws_sqs_queue_policy" "main" {
  queue_url = aws_sqs_queue.model1.id

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "sqspolicy",
  "Statement": [
    {
      "Sid": "First",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "${aws_sqs_queue.model1.arn}",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "${aws_sns_topic.main.arn}"
        }
      }
    }
  ]
}
POLICY
}