# 专门处理文件上传的
import qiniu


access_key = 'yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW'
secret_key = 'bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW'
bucket_name = 'ihome'

def upload_file(data):
    '''上传附件到七牛云
    data:要上传的文件的二进制
    '''
    q = qiniu.Auth(access_key, secret_key)
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, None, data)

    print(ret['key'])

    if info.status_code != 200:
        raise Exception('七牛上传失败')

    return ret['key']
