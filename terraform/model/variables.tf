variable "name" {}
variable "lambda_role" {}
variable "bucket_for_lambda" {}
variable "aws_sns_topic_arn" {}
variable "model_series" {}

variable "aws_lambda_function_key" {
  default = "lambda_function.zip"
}