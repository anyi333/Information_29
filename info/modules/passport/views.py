# 注册和登录
from . import passport_blue
from flask import request,abort,current_app,make_response,jsonify,session
from info.utils.captcha.captcha import captcha
from info import redis_store,constants,response_code,db
import json,re,random,datetime
from info.libs.yuntongxun.sms import CCP
from info.models import User


def register():
    '''注册'''

    # 1.接收参数(手机号,短信验证码,密码明文)
    json_dict = request.json
    mobile = json_dict.get('mobile')
    smscode_client = json_dict.get('smscode')
    password = json_dict.get('password')

    # 2.检验参数(判断是否缺少和手机号是否合法)
    if not all([mobile,smscode_client,password]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少参数')
    if not re.match(r'^[1][3,4,5,7,8][0-9]{9}$',mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机格式错误')

    # 3.查询服务器的短信验证码
    try:
        smscode_server = redis_store.get('SMS:'+ mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR,errmsg='查询短信验证码失败')
    if not smscode_server:
        return jsonify(errno=response_code.RET.NODATA, errmsg='短信验证码不存在')


    # 4.跟客户传入的额短信验证码对比
    if smscode_client != smscode_server:
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='输入短信验证码有误')
    # 5.如果对比成功,就创建User模型对象,并对属性赋值
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # TODO密码需要加密后再存储

    # 记录最后一次登录的时间
    user.last_login = datetime.datetime.now()


    # 6.将模型数据同步到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR,errmsg='保存注册数据失败')

    # 7.保存session,实现状态保持.注册即登录
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name

    # 8.响应注册结果
    return jsonify(errno=response_code.RET.OK,errmsg='注册成功')
@passport_blue.route('/sms_code',methods=['POST'])
def sms_code():
    '''发送短信'''

    # 1.接收参数(手机号,图片验证码,UUID)
    json_str = request.data
    json_dict = json.loads(json_str)
    mobile = json_dict.get('mobile')
    image_code_client = json_dict.get('image_code')
    image_code_id = json_dict.get('image_code_id')

    # 2.校验参数是否齐全,手机号是否合法
    if not all([mobile,image_code_client,image_code_id]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少参数')
    if not re.match(r'^[1][3,4,5,7,8][0-9]{9}$',mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机格式错误')

    # 3.查询服务器存储的图片验证码
    try:
        image_code_server = redis_store.get('ImageCode:' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR,errmsg='查询图片验证码失败')
    if not image_code_server:
        return jsonify(errno=response_code.RET.NODATA,errmsg='图片验证码不存在')

    # 4.跟客户端传入的额图片验证码对比
    if image_code_server != image_code_client:
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='输入验证码有误')
    # 5.如果对比成功,生成短信验证码,并发送短信
    sms_code = '%06d' % random.randint(0,999999)
    result = CCP.send_template_sms(mobile,[sms_code, 5], 1)
    if result != 0:
        return jsonify(errno=response_code.RET.THIRDERR,errmsg='发送短信验证码失败')

    # 6.存储短信验证码到redis,方便注册时比较
    try:
        redis_store.set('SMS:'+mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR,errmsg='保存验证码失败')

    # 7.响应短信验证码发送的结果
    return jsonify(errno=response_code.RET.OK, errmsg='发送验证码成功')


@passport_blue.route('/image_code',methods=['GET'])
def image_code():
    '''提供图片验证'''

    # 1.接收参数(UUID)
    imageCodeId = request.args.get('imageCodeId')

    # 2.校验参数(判断uuid是否为空)
    if not imageCodeId:
        abort(403)
    # 3.生成图片验证码
    name,text,image = captcha.generate_captcha()

    # 4.保存图片验证码到redis
    try:
        redis_store.set('ImageCode:' + imageCodeId,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)

    # 5.修改image的ContentType = 'image/jpg'
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'

    # 6.响应图片验证码
    return image