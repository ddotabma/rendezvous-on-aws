resource "aws_lambda_layer_version" "scikit_layer" {
  depends_on = [aws_s3_bucket_object.main]
  layer_name = "scikit-layer"
  s3_bucket = aws_s3_bucket.lambdas.bucket
  s3_key = aws_s3_bucket_object.main.key
  compatible_runtimes = ["python3.7"]

}

data "archive_file" "function" {
  type = "zip"
  output_path = "scikit-layer.zip"
  source_dir = "../python/layer"
}

resource "aws_s3_bucket_object" "main" {
  bucket = aws_s3_bucket.lambdas.bucket
  key = "scikit-layer.zip"
  source = data.archive_file.function.output_path
  etag = filemd5(data.archive_file.function.output_path)
}