module "lambda_main" {
  source = "./model"
  name = "main"
  lambda_role = aws_iam_role.lambda_main.arn
}