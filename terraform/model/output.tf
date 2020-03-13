output "lambda_arn" {
  value = aws_lambda_function.module_lambda.arn
}


output "lambda_invoke_arn" {
  value = aws_lambda_function.module_lambda.invoke_arn
}


output "lambda_name" {
  value = aws_lambda_function.module_lambda.function_name
}
