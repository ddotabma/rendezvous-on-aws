data "archive_file" "function" {
  type = "zip"
  output_path = "../python/${var.name}/lambda_function.zip"

  source {
    content = templatefile("../python/${var.name}/lambda_function.py", {})
    filename = "lambda_function.py"
  }

  source {
    content = templatefile("../python/${var.name}/model.py", {})
    filename = "model.py"
  }

  source {
    content = templatefile("../python/${var.name}/utils.py", {})
    filename = "utils.py"
  }

}


resource "aws_lambda_function" "module_lambda" {
  function_name = var.name
  s3_bucket = "bdr-rendezvous-lambdas"
  s3_key = "${var.name}/${var.aws_lambda_function_key}"
  handler = "lambda_function.handler"
  role = var.lambda_role
  runtime = "python3.7"
  timeout = 600
  source_code_hash = data.archive_file.function.output_base64sha256

  tags = {
    name = var.name
    model_series = var.model_series
  }
}


resource "aws_s3_bucket_object" "main" {
  bucket = var.bucket_for_lambda
  key = aws_lambda_function.module_lambda.s3_key
  source = data.archive_file.function.output_path
  etag = filemd5(data.archive_file.function.output_path)
}
