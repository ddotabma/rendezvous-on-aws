module "lambda_rendezvous" {
  source = "./model"
  name = "rendezvous"
  lambda_role = aws_iam_role.lambda_rendezvous_role.arn
  bucket_for_lambda = aws_s3_bucket.lambdas.bucket
  aws_sns_topic_arn = aws_sns_topic.main.arn
  model_series = "none"
}


module "lambda_model1" {
  source = "./model"
  name = "model1"
  lambda_role = aws_iam_role.lambda_main.arn
  bucket_for_lambda = aws_s3_bucket.lambdas.bucket
  aws_sns_topic_arn = aws_sns_topic.main.arn
  model_series = "blog"
}


module "lambda_decoy" {
  source = "./model"
  name = "decoy"
  lambda_role = aws_iam_role.lambda_main.arn
  bucket_for_lambda = aws_s3_bucket.lambdas.bucket
  aws_sns_topic_arn = aws_sns_topic.main.arn
  model_series = "blog"
}

module "sqs_decoy" {
  source = "./sqs"
  name = "decoy"
  aws_sns_topic_arn = aws_sns_topic.main.arn
  lambda_arn = module.lambda_decoy.lambda_arn
}

module "sqs_model1" {
  source = "./sqs"
  name = "model1"
  aws_sns_topic_arn = aws_sns_topic.main.arn
  lambda_arn = module.lambda_model1.lambda_arn
}