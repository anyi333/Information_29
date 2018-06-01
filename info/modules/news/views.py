# 新闻详情:收藏,评论,点赞
from . import news_blue
from flask import render_template,session,current_app,abort
from info.models import User,News
from info import constants


@news_blue.route('/detail/<int:news_id>')
def news_detail(news_id):
    '''新闻详情
    1.查询登录用户信息
    2.查询点击排行
    3.查询新闻详情
    '''

    # 1.查询登录用户信息
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        # 表示用户已经登录，然后查询用户的信息
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 2.新闻点击排行展示
    # news_clicks = [News,News,News,News,News,News]
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 3.查询新闻详情
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    # 后续会给404异常准备一个友好的界面
    if not news:
        abort(404)


    context = {
        'user':user,
        'news_clicks':news_clicks,
        'news':news.to_dict()
    }

    # 渲染模板
    return render_template('news/detail.html',context=context)
