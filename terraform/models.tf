module "lambda_main" {
  source = "./model"
  name = "main"
  lambda_role = aws_iam_role.lambda_main.arn
  bucket_for_lambda = aws_s3_bucket.lambdas.bucket
}


module "lambda_model1" {
  source = "./model"
  name = "model1"
  lambda_role = aws_iam_role.lambda_main.arn
  bucket_for_lambda = aws_s3_bucket.lambdas.bucket
}