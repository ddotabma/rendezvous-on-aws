resource "aws_api_gateway_rest_api" "rendezvous" {
  name = "rendezvous"
}


resource "aws_api_gateway_resource" "root" {
  rest_api_id = aws_api_gateway_rest_api.rendezvous.id
  parent_id = aws_api_gateway_rest_api.rendezvous.root_resource_id
  path_part = "testt"
}


resource "aws_api_gateway_method" "root_get" {
  rest_api_id = aws_api_gateway_rest_api.rendezvous.id
  resource_id = aws_api_gateway_resource.root.id
  http_method = "ANY"
  authorization = "NONE"
}


resource "aws_api_gateway_integration" "integration" {
  rest_api_id = aws_api_gateway_rest_api.rendezvous.id
  resource_id = aws_api_gateway_resource.root.id
  http_method = aws_api_gateway_method.root_get.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = module.lambda_rendezvous.lambda_invoke_arn
}

resource "aws_api_gateway_deployment" "test" {
  depends_on = [
    aws_api_gateway_integration.integration]
  rest_api_id = aws_api_gateway_rest_api.rendezvous.id
  stage_name = "test"
}

# Lambda
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id = "AllowExecutionFromAPIGateway"
  action = "lambda:InvokeFunction"
  function_name = module.lambda_rendezvous.lambda_name
  principal = "apigateway.amazonaws.com"
}
