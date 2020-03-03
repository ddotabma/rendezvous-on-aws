resource "aws_sns_topic" "main" {
  name = "main"
}


resource "aws_sns_topic_subscription" "user_updates_sqs_target" {
  topic_arn = aws_sns_topic.main.arn
  protocol = "sqs"
  endpoint = aws_sqs_queue.model1.arn
}
