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

  runtime = "python3.8"

  environment {
    variables = {
      username              = "foo"
      personal_access_token = "bar"
    }
  }
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
  name = "role_image_cleaner_lambda"

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

resource "aws_iam_policy" "this" {
  name        = "policy_image_cleaner_lambda"
  path        = "/"
  description = "IAM policy for image cleaner lambda"

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

resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.this.arn
}
