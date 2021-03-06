data "aws_iam_policy_document" "lambda_main" {
  version = "2012-10-17"
  statement {
    sid = "lambdamain"
    effect = "Allow"
    actions = [
      "sns:Publish",
      "sns:Subscribe"
    ]
    resources = [
      aws_sns_topic.main.arn
    ]
  }
}

data "aws_iam_policy_document" "lambda_sqs" {
  version = "2012-10-17"
  statement {
    sid = "lambdasqs"
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "Kinesis:PutRecord",
      "S3:PutObject",
      "S3:GetObject"
    ]
    resources = [
      "*"
    ]
  }
}

data "aws_iam_policy_document" "lambda_main_assume_role" {
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


resource "aws_iam_role" "lambda_main" {
  name = "lambda_sns_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_main_assume_role.json
}

resource "aws_iam_role_policy" "lambda_main" {
  name = "lambda_merger"
  policy = data.aws_iam_policy_document.lambda_main.json
  role = aws_iam_role.lambda_main.id
}

resource "aws_iam_role_policy" "lambda_sqs" {
  name = "lambda_sqs"
  policy = data.aws_iam_policy_document.lambda_sqs.json
  role = aws_iam_role.lambda_main.id
}

// attachments

resource "aws_iam_role_policy_attachment" "execution_role" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role = aws_iam_role.lambda_main.id
}

