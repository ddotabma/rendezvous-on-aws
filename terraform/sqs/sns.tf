resource "aws_sns_topic_subscription" "sqs_subscription" {
  topic_arn = var.aws_sns_topic_arn
  protocol = "sqs"
  endpoint = aws_sqs_queue.queue.arn
}