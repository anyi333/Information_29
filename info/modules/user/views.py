# 个人中心
from flask import current_app
from flask import g,redirect,url_for,render_template, jsonify,request,session
from info import response_code, db
from . import user_blue
from info.utils.comment import user_login_data


@user_blue.route('/pic_info')
@user_login_data
def pic_info():
    '''设置头像'''

    # 1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'),methods=['GET','POST'])

    # 2.实现GET请求逻辑
    if request.method == 'GET':
        # 构造渲染数据的上下文
        context = {
            'user': user
        }
        # 渲染界面
        return render_template('/news/user_pic_info.html', context=context)

    # 3.POST请求逻辑:修改用户基本信息
    if request.method == "POST":
        pass

@user_blue.route('/base_info',methods=['GET','POST'])
@user_login_data
def base_info():
    '''基本资料'''
    # 1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.实现GET请求逻辑
    if request.method == 'GET':
        # 构造渲染数据的上下文
        context = {
            'user': user
        }
        # 渲染界面
        return render_template('/news/user_base_info.html', context=context)

    # 3.POST请求逻辑:修改用户基本信息
    if request.method == "POST":
        #3.1获取参数(签名,昵称,性别)
        nick_name = request.json.get('nick_name')
        signature = request.json.get('signature')
        gender = request.json.get('gender')

        # 3.2校验参数
        if not all([nick_name,signature,gender]):
            return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少参数')
        if gender not in ['MAN','WOMAN']:
            return jsonify(errno=response_code.RET.PARAMERR,errmsg='参数错误')

        # 3.3修改用户基本信息
        user.nick_name = nick_name
        user.signature = signature
        user.gender = gender

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR,errmsg='修改用户资料失败')

        # 4.注意:修改了昵称以后,记得将状态保持信息中的昵称也修改
        session['nick_name'] = nick_name

        #5.响应修改资料的结果
        return jsonify(errno=response_code.RET.OK,errmsg='修改基本资料成功')

@user_blue.route('/info')
@user_login_data
def user_info():
    '''个人中心入口
    提示:必须是登录用户才能进入
    '''
    # 1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    context = {
        'user':user
    }

    return render_template('news/user.html',context=context)


