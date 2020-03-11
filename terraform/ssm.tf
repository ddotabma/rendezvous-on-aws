resource "aws_ssm_parameter" "foo" {
  name  = "number_of_models"
  type  = "String"
  value = "0"
}