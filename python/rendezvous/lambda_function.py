import boto3
import json
import datetime
import uuid
from model import *
import time
from pprint import pprint
from shared_modules.utils import timer
from shared_modules.response_model import RendezvousMessage, Specifications, BostonRequest, ModelResponse
import traceback

sns = boto3.client('sns')
kinesis = boto3.client("kinesis")
lambda_client = boto3.client("lambda")
ssm = boto3.client('ssm')
stream_name = 'rendezvous'
model_series = "blog"


@timer
def service_count() -> int:
    """Count the number of services by finding all the lambda functions that are tagged with "model_series" """
    functions = LambdaList(**lambda_client.list_functions())
    services = []
    for function in functions.Functions:
        arn = function.FunctionArn
        tags = lambda_client.list_tags(Resource=arn)["Tags"]
        if "model_series" in tags:
            if tags["model_series"] == model_series:
                services.append(function)

    return len(services)


@timer
def get_number_from_ssm() -> int:
    """The number of models is cached in AWS SSM. This is all service discovery that is needed."""
    value = ssm.get_parameter(Name="number_of_models")["Parameter"]["Value"]
    if value == "0":
        value = service_count()
        ssm.put_parameter(Name="number_of_models", Value=str(value), Type='String', Overwrite=True)
    return int(value)


def publish_sns_message(rendezvous_data):
    """Publishing the sns message results in a SQS message that triggers a Lambda model."""
    sns.publish(
        TopicArn='arn:aws:sns:eu-west-1:756285606505:main',
        Message=rendezvous_data
    )


def model_results_from_kinesis(identifier, number_of_services, shard_iterator) -> dict:
    now = datetime.datetime.utcnow()

    model_results: dict = {}
    kinesis_counter = 0

    while (datetime.datetime.utcnow() - now) < datetime.timedelta(seconds=5) and \
            len(model_results) < (number_of_services + 1):
        # +1 since we also want to obtain the data published from the rendezvous lambda
        response = kinesis.get_records(
            ShardIterator=shard_iterator  # response_iterator["ShardIterator"]
        )
        datas = [json.loads(i['Data'].decode()) for i in response['Records']]

        model_results = {i["model"]: i for i in datas if i['uuid'] == identifier and 'model' in i}
        print('cycle ', kinesis_counter, " for kinesis, found", len((model_results)), "results")

        kinesis_counter += 1
        time.sleep(0.2)  # limits the kinesis getRocords to 5 per second, which is the upper limit.
    return model_results


def compare_number_of_results(model_results: dict, number_of_services: int, rendezvous_time: float) -> None:
    if len(model_results) < (number_of_services + 1):
        print("not all models returned on time")
    else:
        print("obtained all results after", time.time() - rendezvous_time, "seconds")
    pprint(model_results)


def handler(event: dict, __):
    print(event)
    try:
        id_ = str(uuid.uuid4())
        rendezvous_time = time.time()
        rendezvous_data = RendezvousMessage(uuid=str(id_),
                                            model="rendezvous",
                                            datetime=str(datetime.datetime.utcnow()),
                                            rendezvous_time=rendezvous_time,
                                            kinesis_stream="rendezvous",
                                            data=Specifications(
                                                request=BostonRequest(**json.loads(event["body"]))

                                            )).json()  # create json string to send to models
        print(rendezvous_data)
        publish_sns_message(rendezvous_data)  # Via SNS and SQS the models are triggered

        resp = kinesis.put_record(StreamName=stream_name,
                                  Data=rendezvous_data,
                                  PartitionKey=id_)  # store the data sent to the models in kinesis.

        response_iterator = kinesis.get_shard_iterator(
            StreamName=stream_name,
            ShardId=resp["ShardId"],
            ShardIteratorType="AT_TIMESTAMP",
            Timestamp=datetime.datetime.utcnow()
        )

        number_of_services = get_number_from_ssm()  # get the cached number of registered models

        model_results = model_results_from_kinesis(identifier=id_,
                                                   number_of_services=number_of_services,
                                                   shard_iterator=response_iterator["ShardIterator"])

        compare_number_of_results(model_results=model_results,
                                  number_of_services=number_of_services,
                                  rendezvous_time=rendezvous_time)

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(dict(**model_results, total_time=time.time() - rendezvous_time))
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(dict(traceback=traceback.format_exc(), message=str(e)))
        }


if __name__ == "__main__":
    print(handler(
        {'resource': '/root', 'path': '/root', 'httpMethod': 'POST', 'headers': {'Accept': '*/*',
                                                                                 'Accept-Encoding': 'gzip, deflate, br',
                                                                                 'Cache-Control': 'no-cache',
                                                                                 'CloudFront-Forwarded-Proto': 'https',
                                                                                 'CloudFront-Is-Desktop-Viewer': 'true',
                                                                                 'CloudFront-Is-Mobile-Viewer': 'false',
                                                                                 'CloudFront-Is-SmartTV-Viewer': 'false',
                                                                                 'CloudFront-Is-Tablet-Viewer': 'false',
                                                                                 'CloudFront-Viewer-Country': 'NL',
                                                                                 'Content-Type': 'application/json',
                                                                                 'Host': 'pe47ygzcm1.execute-api.eu-west-1.amazonaws.com',
                                                                                 'Postman-Token': '8aab6fdc-20c4-4428-a619-3f76097ebc3d',
                                                                                 'User-Agent': 'PostmanRuntime/7.24.0',
                                                                                 'Via': '1.1 b9a91b9002d4fb924a73a6172edb4dc8.cloudfront.net (CloudFront)',
                                                                                 'X-Amz-Cf-Id': 'XTOwpjqTeFN6zU5PTp12FsIKNg75r893549anznA6e-1Tb_zMGe4Dw==',
                                                                                 'X-Amzn-Trace-Id': 'Root=1-5e7e0665-ba5fc5dca9401ef8a6e81dba',
                                                                                 'X-Forwarded-For': '94.210.13.178, 70.132.14.147',
                                                                                 'X-Forwarded-Port': '443',
                                                                                 'X-Forwarded-Proto': 'https'},
         'multiValueHeaders': {
             'Accept': ['*/*'], 'Accept-Encoding': ['gzip, deflate, br'], 'Cache-Control': ['no-cache'],
             'CloudFront-Forwarded-Proto': ['https'], 'CloudFront-Is-Desktop-Viewer': ['true'],
             'CloudFront-Is-Mobile-Viewer': ['false'], 'CloudFront-Is-SmartTV-Viewer': ['false'],
             'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-Country': ['NL'],
             'Content-Type': ['application/json'], 'Host': ['pe47ygzcm1.execute-api.eu-west-1.amazonaws.com'],
             'Postman-Token': ['8aab6fdc-20c4-4428-a619-3f76097ebc3d'], 'User-Agent': ['PostmanRuntime/7.24.0'],
             'Via': ['1.1 b9a91b9002d4fb924a73a6172edb4dc8.cloudfront.net (CloudFront)'],
             'X-Amz-Cf-Id': ['XTOwpjqTeFN6zU5PTp12FsIKNg75r893549anznA6e-1Tb_zMGe4Dw=='],
             'X-Amzn-Trace-Id': ['Root=1-5e7e0665-ba5fc5dca9401ef8a6e81dba'],
             'X-Forwarded-For': ['94.210.13.178, 70.132.14.147'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': [
                 'https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None,
         'pathParameters': None, 'stageVariables': None, 'requestContext': {
            'resourceId': '9uimp1', 'resourcePath': '/root', 'httpMethod': 'POST',
            'extendedRequestId': 'KDXv3HHmjoEFaCQ=',
            'requestTime': '27/Mar/2020:13:57:57 +0000', 'path': '/rendezvous/root', 'accountId': '756285606505',
            'protocol': 'HTTP/1.1', 'stage': 'rendezvous', 'domainPrefix': 'pe47ygzcm1',
            'requestTimeEpoch': 1585317477455,
            'requestId': 'a950eef0-7baa-4a91-a692-a3e084e99510',
            'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None,
                         'sourceIp': '94.210.13.178', 'principalOrgId': None, 'accessKey': None,
                         'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None,
                         'userAgent': 'PostmanRuntime/7.24.0', 'user': None},
            'domainName': 'pe47ygzcm1.execute-api.eu-west-1.amazonaws.com',
            'apiId': 'pe47ygzcm1'},
         'body': '{\n    "CRIM": 0.31533,\n    "ZN": 0,\n    "INDUS": 6.2,\n    "CHAS": 0,\n    "NOX": 0.504,\n    "RM": 8.266,\n    "AGE": 78.3,\n    "DIS": 2.8944,\n    "RAD": 8,\n    "TAX": 307,\n    "PTRATIO": 17.4,\n    "B": 385.05,\n    "LSTAT": 4.14\n}',
         'isBase64Encoded': False}, None))
