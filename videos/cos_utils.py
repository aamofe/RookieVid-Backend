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


def delete_object(key):
    client, bucket_name, bucket_region = get_cos_client()
    #.cssg-snippet-body-start:[delete-object]
    response = client.delete_object(
        Bucket=bucket_name,
        Key=key
    )


def delete_object_comp():
    # .cssg-snippet-body-start:[delete-object-comp]
    # 删除object
    client, bucket_name, bucket_region = get_cos_client()
    response = client.delete_object(
        Bucket='examplebucket-1250000000',
        Key='exampleobject'
    )
    # 删除多个object
    ## deleteObjects
    response = client.delete_objects(
        Bucket='examplebucket-1250000000',
        Delete={
            'Object': [
                {
                    'Key': 'exampleobject1',
                },
                {
                    'Key': 'exampleobject2',
                },
            ],
            'Quiet': 'true' | 'false'
        }
    )