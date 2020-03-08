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
      "Kinesis:PutRecord"
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

resource "aws_iam_policy" "lambda_main" {
  name = "lambda_merger"
  policy = data.aws_iam_policy_document.lambda_main.json
}

resource "aws_iam_policy" "lambda_sqs" {
  name = "lambda_sqs"
  policy = data.aws_iam_policy_document.lambda_sqs.json
}

// attachments

resource "aws_iam_role_policy_attachment" "lambda_main" {
  policy_arn = aws_iam_policy.lambda_main.arn
  role = aws_iam_role.lambda_main.name
}


resource "aws_iam_role_policy_attachment" "lambda_sqs" {
  policy_arn = aws_iam_policy.lambda_sqs.arn
  role = aws_iam_role.lambda_main.name
}


resource "aws_iam_role_policy_attachment" "execution_role" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role = aws_iam_role.lambda_main.id
}

