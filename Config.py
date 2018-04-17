class Config:
    aws_key = "IAM ACCESS KEY"
    aws_secret = "IAM SECRET ACCESS KEY"
    lambda_function_arn = "YOUR LAMBDA FUNCTION ARN"

    @classmethod
    def get_aws_key(cls):
        return cls.aws_key

    @classmethod
    def get_aws_secret(cls):
        return cls.aws_secret

    @classmethod
    def get_lambda_uri(cls):
        return cls.lambda_function_arn
