from aws_xray_sdk.core import patch
import os
# if os.environ.get('stage') != "test":
#     libraries = ('boto3', 'pynamodb')
#     # x-ray에서 boto3 리소스에 대해 캡쳐
#     patch(libraries)
