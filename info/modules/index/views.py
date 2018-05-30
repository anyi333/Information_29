# 主页模块
from . import index_blue
from flask import render_template,current_app,session
from info.models import User


@index_blue.route('/')
def index():
    """主页"""
    # 当用户已登录展示"用户名 退出",未登录展示"登录  注册"
    # 1.处理网页右上角的用户展示数据
    user_id = session.get('user_id',None)
    user = None
    if user_id:
        # 表示用户已经登录,然后查询用户的信息
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 构造渲染模板的上下文数据
    context = {
        'user':user
    }

    # 渲染主页
    return render_template('news/index.html',context=context)


@index_blue.route('/favicon.ico', methods=['GET'])
def favicon():
    """title左侧图标"""
    # return 'Users/zhangjie/Desktop/Information_29/info/static/news/favicon.ico'
    return current_app.send_static_file('news/favicon.ico')