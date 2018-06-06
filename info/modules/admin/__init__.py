from flask import Blueprint
from flask import redirect
from flask import session
from flask import url_for

admin_blue = Blueprint('admin', __name__,url_prefix='/admin')

from . import views

def check_admin():
    '''验证用户身份是否时admin'''
    is_admin = session.get('is_admin',False)

    # 判断是否是管理员
    if not is_admin:
        return redirect(url_for('index.index'))
