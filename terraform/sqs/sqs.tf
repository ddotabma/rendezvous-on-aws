resource "aws_sqs_queue" "queue" {
  name = var.name
  delay_seconds = 0
  max_message_size = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10

  tags = {
    model = "yes",
    name = var.name
  }
}

resource "aws_sqs_queue_policy" "main" {
  queue_url = aws_sqs_queue.queue.id
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
      "Resource": "${aws_sqs_queue.queue.arn}",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "${var.aws_sns_topic_arn}"
        }
      }
    }
  ]
}
POLICY
}