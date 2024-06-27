# test_imports.py
from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda, 
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct


print("Imports successful")

class CdkAppStack(Stack):

    _lambda_code= """
    def handler(event, context):
        pass 
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = dynamodb.Table(
            self, "Table",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        # with open('assets/_lamda_code.py', 'r') as fd:
        #     code = fd.read()

        function = _lambda.Function(
            self, "Function",
            handler="_lambda_code.handler",
            timeout=Duration.minutes(5),
            runtime=_lambda.Runtime.PYTHON_3_12,
            function_name="query_ddb",
            code=_lambda.Code.from_asset("assets/func_query_ddb"),
            memory_size=256,
            environment={"TABLE": table.table_name }
        )

        table.grant_read_data(function)

        CfnOutput(
            self, "OutputTableARN",
            value=table.table_arn,
            key="TableARN",
        )


    