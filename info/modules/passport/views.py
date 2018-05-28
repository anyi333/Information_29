# 注册和登录
from . import passport_blue
from flask import request

@passport_blue.route('/image_code',methods=['GET'])
def image_code():
    '''提供图片验证'''

    print(request.url)
    pass

