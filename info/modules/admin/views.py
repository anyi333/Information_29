# 后台管理
import datetime
import time
from flask import abort, jsonify
from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from info import constants, db
from info import response_code
from info.models import User, News
from info.modules import user
from info.utils.comment import user_login_data
from . import admin_blue



@admin_blue.route('/news_review_action',methods=['POST'])
def news_review_action():
    '''审核新闻实现'''

    # 1.接受参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    # 2.校验参数
    if not all([news_id, action]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少参数')
    if action not in['accept','reject']:
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='参数错误')

    # 3.查询待审核的新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR,errmsg='查询新闻数据失败')

    if not news:
        return jsonify(errno=response_code.RET.NODATA,errmsg='新闻不存在')

    # 4.实现审核逻辑
    if action == 'accept':
        #通过
        news.status = 0
    else:
        # 拒绝通过
        news.status = -1
        # 补充拒绝原因
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=response_code.RET.NODATA, errmsg='缺少拒绝理由')
        news.reason = reason

    # 5.同步数据库
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR,errmsg='保存数据失败')

    # 6.响应结果
    return jsonify(errno=response_code.RET.OK,errmsg='OK')

@admin_blue.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    '''待审核新闻列表'''

    # 1.查询出要审核的新闻的详情
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    if not news:
        abort(404)
    # 2.构造渲染数据
    context = {
        'news':news.to_dict()
    }

    return render_template('admin/news_review_detail.html',context=context)



@admin_blue.route('/news_review')
def news_review():
    '''后台新闻审核列表'''
    # 1.接受参数
    page = request.args.get('p', '1')
    keyword = request.args.get('keyword')

    # 2.校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'
    # 3.分页查询用户列表,管理员除外
    news_list = []
    current_page = 1
    total_page = 1

    try:
        if keyword:
            paginate = News.query.filter(News.title.contains(keyword),News.status!=0).order_by(News.create_time.desc()).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
        else:
            paginate = News.query.filter(News.status != 0).order_by(News.create_time.desc()).paginate(page,
                                                                                                      constants.ADMIN_NEWS_PAGE_MAX_COUNT,
                                                                                                      False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    # 4.构造渲染数据
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    context = {
        'news_list': news_dict_list,
        'current_page': current_page,
        'total_page': total_page
    }
    # 5.响应结果
    return render_template('admin/news_review.html',context=context)


@admin_blue.route('/user_list')
def user_list():
    '''用户列表'''

    # 1.接受参数
    page = request.args.get('p','1')

    # 2.校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'

    # 3.分页查询用户列表,管理员除外
    users = []
    current_page = 1
    total_page = 1

    try:
        paginate = User.query.filter(User.is_admin==False).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    user_dict_list = []
    for user in users:
        user_dict_list.append(user.to_admin_dict())

    # 4.构造渲染数据
    context = {
        'users':user_dict_list,
        'current_page':current_page,
        'total_page':total_page
    }

    return render_template('admin/user_list.html',context=context)



@admin_blue.route('/user_count')
def user_count():
    '''用户量统计 '''
    # 用户总数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 月新增数
    month_count = 0
    # 计算每月开始时间 比如：2018-06-01 00：00：00
    t = time.localtime()
    # 计算每月开始时间字符串
    month_begin = '%d-%02d-01' % (t.tm_year, t.tm_mon)
    # 计算每月开始时间对象
    month_begin_date = datetime.datetime.strptime(month_begin, '%Y-%m-%d')
    try:
        month_count = User.query.filter(User.is_admin == False, User.create_time > month_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 日新增数
    day_count = 0
    # 计算当天的开始时间 比如：2018-06-04 00：00：00
    t = time.localtime()
    day_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    day_begin_date = datetime.datetime.strptime(day_begin, '%Y-%m-%d')
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 每日的用户登录活跃量
    # 存放X轴的时间节点
    active_date = []
    # 存放Y轴的登录量的节点
    active_count = []

    # 查询今天开始的时间 06月04日 00:00:00
    # 获取当天开始时时间字符串
    today_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    # 获取当前开始时时间对象
    today_begin_date = datetime.datetime.strptime(today_begin, '%Y-%m-%d')

    for i in range(0, 15):
        # 计算一天开始
        begin_date = today_begin_date - datetime.timedelta(days=i)
        # 计算一天结束
        end_date = today_begin_date - datetime.timedelta(days=(i - 1))

        # 将X轴对应的开始时间记录
        # strptime : 将时间字符串转成时间对象
        # strftime : 将时间对象转成时间字符串
        active_date.append(datetime.datetime.strftime(begin_date, '%Y-%m-%d'))

        # 查询当天的用户登录量
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login < end_date).count()
            active_count.append(count)
        except Exception as e:
            current_app.logger.error(e)

    # 反转列表
    active_count.reverse()
    active_date.reverse()

    context = {
        'total_count':total_count,
        'month_count':month_count,
        'day_count':day_count,
        'active_date':active_date,
        'active_count':active_count
    }


    return render_template('admin/user_count.html',context=context)


@admin_blue.route('/')
@user_login_data
def admin_index():
    '''主页'''
    # 获取登录用户的信息
    user = g.user
    if not user:
        return redirect(url_for('admin.admin_login'))
    # 构造渲染的数据
    context = {
        'user':user.to_dict() if user else None
    }
    # 渲染模板
    return render_template('admin/index.html',context=context)


@admin_blue.route('/login',methods=['GET','POST'])
def admin_login():
    '''登录'''

    # GET:提供登录界面
    if request.method == 'GET':
        # 获取登录用户信息.如果用户已经登录的,直接进入到主页
        user_id = session.get('user_id',None)
        is_admin = session.get('is_admin',False)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))

        return render_template('admin/login.html')

    # POST:实现登录的后端业务逻辑
    if request.method == 'POST':
        # 1.获取参数
        username = request.form.get('username')
        password = request.form.get('password')

        # 2.校验参数
        if not all([username,password]):
            return render_template('admin/login.html',errmsg='缺少参数')

        # 3.查询出当前要登录的用户是否存在
        try:
            user = User.query.filter(User.nick_name==username).first()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/login.html',errmsg='查询用户数据失败')
        if not user:
            return render_template('admin/login.html', errmsg='用户名或密码错误')

        # 4.对比当前要登录的用户的密码
        if not user.check_password(password):
            return render_template('admin/login.html', errmsg='用户名或密码错误')

        # 5.将状态保持信息写入session
        session['user_id'] = user.id
        session['nick_name'] = user.nick_name
        session['mobile'] = user.mobile
        session['is_admin'] = user.is_admin

        # 6.响应登录结果
        return redirect(url_for('admin.admin_index'))
