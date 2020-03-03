resource "aws_s3_bucket" "lambdas" {
  bucket = "bdr-rendezvous-lambdas"
}

resource "aws_s3_bucket_object" "main" {
  bucket = aws_s3_bucket.lambdas.bucket
  key = "main/lambda_function.zip"
  source = "../python/main/lambda_function.zip"

  etag = filemd5("../python/main/lambda_function.zip")

}