import boto3
import json
import datetime
import uuid
from model import *
import time
from pprint import pprint
from shared_modules.utils import timer
from shared_modules.response_model import RendezvousMessage, Specifications, BostonRequest, ModelResponse
from dataclasses import asdict

sns = boto3.client('sns')
kinesis = boto3.client("kinesis")
lambda_client = boto3.client("lambda")
ssm = boto3.client('ssm')
stream_name = 'rendezvous'
model_series = "blog"


@timer
def service_count():
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
    value = ssm.get_parameter(Name="number_of_models")["Parameter"]["Value"]
    if value == "0":
        value = service_count()
        ssm.put_parameter(Name="number_of_models", Value=str(value), Type='String', Overwrite=True)
    return int(value)


def publish_sns_message(rendezvous_data, stream_name):
    sns.publish(
        TopicArn='arn:aws:sns:eu-west-1:756285606505:main',
        Message=rendezvous_data
    )


def handler(event, __):
    print(event["queryStringParameters"])
    id_ = str(uuid.uuid4())
    rendezvous_time = time.time()
    rendezvous_data = json.dumps(asdict(RendezvousMessage(uuid=str(id_),
                                                          model="rendezvous",
                                                          datetime=str(datetime.datetime.utcnow()),
                                                          rendezvous_time=rendezvous_time,
                                                          data=Specifications(
                                                              request=BostonRequest(**json.loads(event["body"])),
                                                              kinesis_stream="rendezvous"
                                                          ))))
    print(rendezvous_data)
    publish_sns_message(rendezvous_data)
    now = datetime.datetime.utcnow()

    print("Start putting kinesis record after", time.time() - rendezvous_time, "seconds")

    resp = kinesis.put_record(StreamName=stream_name,
                              Data=rendezvous_data,
                              PartitionKey="rendezvous")

    print("Start getting shard iterator kinesis iterator after", time.time() - rendezvous_time, "seconds")

    response_iterator = kinesis.get_shard_iterator(
        StreamName=stream_name,
        ShardId=resp["ShardId"],
        ShardIteratorType="AT_TIMESTAMP",
        Timestamp=now
    )

    print("Done getting shard iterator kinesis iterator after", time.time() - rendezvous_time, "seconds")

    this_call = {}
    services = get_number_from_ssm()
    kinesis_counter = 0

    print("Starting kinesis loop after", time.time() - rendezvous_time, "seconds")

    while (datetime.datetime.utcnow() - now) < datetime.timedelta(seconds=5) and len(this_call) < (services + 1):
        response = kinesis.get_records(
            ShardIterator=response_iterator["ShardIterator"]
        )
        datas = [json.loads(i['Data'].decode()) for i in response['Records']]
        this_call = {i["model"]: i for i in datas if i['uuid'] == id_ and 'model' in i}
        print('cycle ', kinesis_counter, " for kinesis, found", len((this_call)), "results")
        kinesis_counter += 1
        time.sleep(0.2)

    if len(this_call) < (services + 1):
        print("not all models returned on time")
    else:
        print("obtained all results after", time.time() - rendezvous_time, "seconds")
    pprint(this_call)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(dict(**this_call, total_time=time.time() - rendezvous_time))
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
