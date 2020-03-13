resource "aws_s3_bucket" "lambdas" {
  bucket = "bdr-rendezvous-lambdas"
}

resource "aws_s3_bucket" "trained_models" {
  bucket = "bdr-rendezvous-model"
}
