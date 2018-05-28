# 主页模块
from . import index_blue
from flask import render_template,current_app


@index_blue.route('/')
def index():
    """主页"""

    # 渲染主页
    return render_template('news/index.html')


@index_blue.route('/favicon.ico', methods=['GET'])
def favicon():
    """title左侧图标"""
    # return 'Users/zhangjie/Desktop/Information_29/info/static/news/favicon.ico'
    return current_app.send_static_file('news/favicon.ico')