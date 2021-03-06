resource "aws_api_gateway_rest_api" "rendezvous" {
  name = "rendezvous"
}


resource "aws_api_gateway_resource" "root" {
  rest_api_id = aws_api_gateway_rest_api.rendezvous.id
  parent_id = aws_api_gateway_rest_api.rendezvous.root_resource_id
  path_part = "root"
}


resource "aws_api_gateway_method" "root_any" {
  rest_api_id = aws_api_gateway_rest_api.rendezvous.id
  resource_id = aws_api_gateway_resource.root.id
  http_method = "ANY"
  authorization = "NONE"
}


resource "aws_api_gateway_integration" "integration" {
  rest_api_id = aws_api_gateway_rest_api.rendezvous.id
  resource_id = aws_api_gateway_resource.root.id
  http_method = aws_api_gateway_method.root_any.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = module.lambda_rendezvous.lambda_invoke_arn
}

resource "aws_api_gateway_deployment" "test" {
  depends_on = [
    aws_api_gateway_integration.integration]
  rest_api_id = aws_api_gateway_rest_api.rendezvous.id
  stage_name = "rendezvous"
}

//resource "aws_api_gateway_stage" "test" {
//  stage_name = "test_stage"
//  rest_api_id = aws_api_gateway_rest_api.rendezvous.id
//  deployment_id = aws_api_gateway_deployment.test.id
//}

# Lambda
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id = "AllowExecutionFromAPIGateway"
  action = "lambda:InvokeFunction"
  function_name = module.lambda_rendezvous.lambda_name
  principal = "apigateway.amazonaws.com"
}

resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id = aws_api_gateway_rest_api.rendezvous.id
  resource_id = aws_api_gateway_resource.root.id
  http_method = aws_api_gateway_method.root_any.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "rendezvous" {
  rest_api_id = aws_api_gateway_rest_api.rendezvous.id
  resource_id = aws_api_gateway_resource.root.id
  http_method = aws_api_gateway_method.root_any.http_method
  status_code = aws_api_gateway_method_response.response_200.status_code

  response_templates = {
    "application/json" = <<EOF
    $inputRoot.body
EOF
  }
}