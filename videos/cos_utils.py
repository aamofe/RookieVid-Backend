import os

from qcloud_cos import CosConfig, CosS3Client


def get_cos_client():

    secret_id = 'AKIDOk2PhswtjUCpMm6JP1Z5Sju0sfL5kIj7'     # 用户的 SecretId
    secret_key = 'Vq6HsNm5IRp6LBzhImBWp8Sjx6A83vje'   # 用户的 SecretKey
    bucket_name = 'aamofe-1315620690'
    region = 'ap-beijing'                       # COS桶所属的地域
    token = None                                # 如果使用临时密钥，填写对应的token，否则为None
    scheme = 'https'                            # 访问协议，https或http

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)
    return client, bucket_name, region



