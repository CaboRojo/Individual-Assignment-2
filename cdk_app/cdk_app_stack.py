from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_iam as iam, 
    App
)
from constructs import Construct

class CdkAppStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create DynamoDB table for items
        table = dynamodb.Table(
            self, "IE_Courses",
            table_name="IE_Courses",
            partition_key=dynamodb.Attribute(name="ItemId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Course", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Add Global Secondary Index for Course
        table.add_global_secondary_index(
            index_name="Course-index",
            partition_key=dynamodb.Attribute(name="Course", type=dynamodb.AttributeType.STRING)
        )

        # Create DynamoDB table for counter
        counter_table = dynamodb.Table(
            self, "CounterTable",
            partition_key=dynamodb.Attribute(name="CounterName", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        environment = {
            'TABLE': table.table_name,
            'COUNTER_TABLE': counter_table.table_name
        }

        # Define Lambda functions
        add_item_lambda = self.create_lambda("AddItemFunction", "add_item.handler", environment)
        get_item_lambda = self.create_lambda("GetItemFunction", "get_item.handler", environment)
        delete_item_lambda = self.create_lambda("DeleteItemFunction", "delete_item.handler", environment)
        get_all_items_lambda = self.create_lambda("GetAllItemsFunction", "get_all_items.handler", environment)
        get_items_by_course_lambda = self.create_lambda("GetItemsByCourseFunction", "get_items_by_course.handler", environment)
        get_items_by_year_lambda = self.create_lambda("GetItemsByYearFunction", "get_items_by_year.handler", environment)

        # Grant granular permissions to Lambda functions
        table.grant_write_data(add_item_lambda)
        table.grant_read_data(get_item_lambda)
        table.grant_write_data(delete_item_lambda)
        table.grant_read_data(get_all_items_lambda)
        table.grant_read_data(get_items_by_course_lambda)
        table.grant_read_data(get_items_by_year_lambda)
        counter_table.grant_read_write_data(add_item_lambda)

        # Additional permissions for querying the secondary index
        get_items_by_course_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:Query"],
                resources=[f"{table.table_arn}/index/Course-index"]
            )
        )

        # Create API Gateway
        api = apigateway.RestApi(
            self, "knowledgeCatalogApi",
            rest_api_name="Knowledge Catalog Service",
            description="This service serves knowledge catalog."
        )

        # Define API Gateway integrations
        add_item_integration = apigateway.LambdaIntegration(add_item_lambda)
        get_item_integration = apigateway.LambdaIntegration(get_item_lambda)
        delete_item_integration = apigateway.LambdaIntegration(delete_item_lambda)
        get_all_items_integration = apigateway.LambdaIntegration(get_all_items_lambda)
        get_items_by_course_integration = apigateway.LambdaIntegration(get_items_by_course_lambda)
        get_items_by_year_integration = apigateway.LambdaIntegration(get_items_by_year_lambda)

        # Define API Gateway resources and methods
        api.root.add_resource("add-item").add_method("POST", add_item_integration)
        api.root.add_resource("get-item").add_resource("{id}").add_method("GET", get_item_integration)
        api.root.add_resource("delete-item").add_resource("{id}").add_method("DELETE", delete_item_integration)
        api.root.add_resource("get-all-items").add_method("GET", get_all_items_integration)
        api.root.add_resource("get-items-by-course").add_resource("{course}").add_method("GET", get_items_by_course_integration)
        api.root.add_resource("get-items-by-year").add_resource("{year}").add_method("GET", get_items_by_year_integration)

        # Output the table ARN
        CfnOutput(self, "OutputTableARN", value=table.table_arn)

    def create_lambda(self, id, handler, environment):
        return _lambda.Function(
            self, id,
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler=handler,
            code=_lambda.Code.from_asset("assets/func_query_ddb"),
            timeout=Duration.minutes(5),
            memory_size=256,
            environment=environment
        )

app = App()
CdkAppStack(app, "KnowledgeCatalogStack")
app.synth()
