import boto3
import os
def auth(service):
    service = boto3.client(
        service_name = service, 
        region_name='ap-northeast-2', 
        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    )