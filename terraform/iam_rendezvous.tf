
data "aws_iam_policy_document" "lambda_rendezvous_assume" {
  statement {
    actions = [
      "sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",]
    }
  }
}

data "aws_iam_policy_document" "lambda_rendezvous" {
  version = "2012-10-17"
  statement {
    sid = "lambdasqs"
    effect = "Allow"
    actions = [
      "sns:Publish",
      "Kinesis:PutRecord",
      "Kinesis:GetRecords",
      "Kinesis:ListShards",
      "Kinesis:GetShardIterator"
    ]
    resources = [
      "*"
    ]
  }
}

resource "aws_iam_policy" "lambda_rendezvous" {
  name = "lambda_rendezvous_policy"
  policy = data.aws_iam_policy_document.lambda_rendezvous.json
}

resource "aws_iam_role" "lambda_rendezvous_role" {
  name = "lambda_rendezvous_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_rendezvous_assume.json
}

resource "aws_iam_role_policy_attachment" "sns_kinesis_rendezvous" {
  policy_arn = aws_iam_policy.lambda_rendezvous.arn
  role = aws_iam_role.lambda_rendezvous_role.id
}

resource "aws_iam_role_policy_attachment" "execution_role_rendezvous" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role = aws_iam_role.lambda_rendezvous_role.id
}