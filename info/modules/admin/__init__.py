from flask import Blueprint
from flask import Flask
from flask import redirect
from flask import request
from flask import session
from flask import url_for


admin_blue = Blueprint('admin', __name__,url_prefix='/admin')
from . import views
'''
def check_admin():
    #验证用户身份是否时admin
    is_admin = session.get('is_admin',False)
    # 1.判断是否是管理员,只有管理员才能进入后台管理
    # 2.当无论哪种用户访问后台,管理的登陆界面都可以正常进入
         #2.1如果是前台用户,可以登录,但是登录后续的操作会被卡住
         #2.2如果时后台用户,可以登录
    # is_admin默认是false  真 and 假 = 假 所以不执行,不能进入管理员界面
    # 3.如果管理员进入后台界面.又误入前台界面,会留下session  is_admin=True  所以在password中要清除session
    if not is_admin and not request.url.endswith('admin/login'):
        return redirect(url_for('index.index'))
'''
app = Flask(__name__)

@admin_blue.before_request
def before_request():
    # 判断如果不是登录页面的请求
    if not request.url.endswith(url_for("admin.admin_login")):
        user_id = session.get("user_id")
        is_admin = session.get("is_admin", False)

        if not user_id or not is_admin:
            # 判断当前是否有用户登录，或者是否是管理员，如果不是，直接重定向到项目主页
            return redirect('/')