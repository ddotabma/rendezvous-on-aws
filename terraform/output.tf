output "sns-main" {
  value = aws_sns_topic.main.arn
}

output "sqs-model1-id" {
  value = aws_sqs_queue.model1.id
}