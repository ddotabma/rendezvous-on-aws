data "aws_iam_policy_document" "lambda_main" {
  version = "2012-10-17"
  statement {
    sid = ""
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


data "aws_iam_policy_document" "lambda_main_assume_role" {
  statement {
    actions = [
      "sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}


resource "aws_iam_role" "lambda_main" {
  assume_role_policy = data.aws_iam_policy_document.lambda_main_assume_role.json
}


resource "aws_iam_policy" "lambda_main" {
  name = "lambda_merger"
  policy = data.aws_iam_policy_document.lambda_main.json
}

resource "aws_iam_role_policy_attachment" "lambda_merger" {
  policy_arn = aws_iam_policy.lambda_main.arn
  role = aws_iam_role.lambda_main.name
}


