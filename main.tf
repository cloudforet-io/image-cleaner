##################################
# cloudwatch
##################################

resource "aws_cloudwatch_event_rule" "this" {
  name        = "image_clean_schedule"
  description = "image clean schedule"

  schedule_expression = var.schedule
}

resource "aws_cloudwatch_event_target" "this" {
  target_id = "image_clean_schedule"
  rule      = aws_cloudwatch_event_rule.this.name
  arn       = aws_lambda_function.this.arn
}

##################################
# lambda
##################################

data "archive_file" "lambda_zip" {
  type = "zip"
  source_file = "./src/image_cleaner.py"
  output_path = "./src/lambda_function.zip"
}

resource "aws_lambda_function" "this" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = "image_cleaner"
  role          = aws_iam_role.this.arn
  handler       = "image_cleaner.lambda_handler"

  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.8"
  timeout          = "60"
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.this.arn
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${aws_lambda_function.this.function_name}"
  retention_in_days = 14
}

##################################
# IAM
##################################

resource "aws_iam_role" "this" {
  name = "image_cleaner_lambda_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "logging" {
  name        = "image_cleaner_lambda_logging_policy"
  path        = "/"
  description = "IAM policy for image cleaner lambda logging"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "logging" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.logging.arn
}

resource "aws_iam_policy" "ssm" {
  name        = "image_cleaner_lambda_ssm_policy"
  path        = "/"
  description = "IAM policy for image cleaner lambda ssm"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "ssm:GetParameters"
      ],
      "Resource": "arn:aws:ssm:*:*:parameter/*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.ssm.arn
}
