data "archive_file" "function" {
  type        = "zip"
  source_file = "../python/${var.name}/lambda_function.py"
  output_path = "../python/${var.name}/lambda_function.zip"
}

resource "aws_lambda_function" "module_lambda" {
  function_name = var.name
  s3_bucket = "bdr-rendezvous-lambdas"
  s3_key = "${var.name}/lambda_function.zip"
  handler = "lambda_function.handler"
  role = var.lambda_role
  runtime = "python3.7"
  source_code_hash = data.archive_file.function.output_base64sha256
}