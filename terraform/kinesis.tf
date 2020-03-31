resource "aws_kinesis_stream" "rendezvous" {
  name = "rendezvous"
  shard_count = 1
  shard_level_metrics = [
    "IncomingBytes",
    "OutgoingBytes"
  ]
}

data "aws_iam_policy_document" "firehose" {
  version = "2012-10-17"
  statement {
    sid = "fh"
    effect = "Allow"
    actions = [
      "s3:AbortMultipartUpload",
      "s3:GetBucketLocation",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:ListBucketMultipartUploads",
      "s3:PutObject"
    ]
    resources = [
      aws_s3_bucket.bdr-blog-firehose.arn,
      "${aws_s3_bucket.bdr-blog-firehose.arn}/*"
    ]
  }
}

data "aws_iam_policy_document" "firehose_assume" {
  statement {
    actions = [
      "sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "firehose.amazonaws.com",]
    }
  }
}

resource "aws_iam_role" "firehose" {
  name = "firehose"
  assume_role_policy = data.aws_iam_policy_document.firehose_assume.json
}

resource "aws_iam_role_policy" "firehose" {
  name = "firehose"
  policy = data.aws_iam_policy_document.firehose.json
  role = aws_iam_role.firehose.id
}

resource "aws_s3_bucket" "bdr-blog-firehose" {
  bucket = "bdr-blog-firehose"
  acl = "private"
}

resource "aws_kinesis_firehose_delivery_stream" "firehose" {
  name = "rendezvous"
  destination = "s3"

  s3_configuration {
    role_arn = "${aws_iam_role.firehose.arn}"
    bucket_arn = "${aws_s3_bucket.bdr-blog-firehose.arn}"
  }
}