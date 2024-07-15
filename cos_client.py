# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging

from dotenv import load_dotenv

from image_storage_util import upload_jpg_to_blob

load_dotenv()

bucket = os.getenv('Bucket')
region = os.getenv('Region')

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
# 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_id = os.environ['COS_SECRET_ID']
# 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_key = os.environ['COS_SECRET_KEY']
# 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
token = None
scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

config = CosConfig(Region=region, SecretId=secret_id,
                   SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)


def getFileByNameFromStorage(fileName):
    response = client.get_object(
        Bucket=bucket,
        Key=fileName
    )
    file_stream = response['Body'].get_raw_stream()
    file_bytes = file_stream.read()
    return file_bytes


def getFileByNameToLocal(fileName):
    response = client.get_object(
        Bucket=bucket,
        Key=fileName
    )
    response['Body'].get_stream_to_file('output.jpg')


def getFileFromCosAndUploadToBlob(fileName):
    response = client.get_object(
        Bucket=bucket,
        Key=fileName
    )
    file_stream = response['Body'].get_raw_stream()
    file_bytes = file_stream.read()
    return upload_jpg_to_blob(file_bytes)


def signForUpload(key):
    response = client.get_auth(
        Method='PUT',
        Bucket=bucket,
        Key=key,
        Expires=3600
    )

    return response


if __name__ == "__main__":
    print(getFileFromCosAndUploadToBlob("file/20240715/20240715_917343.jpg"))
