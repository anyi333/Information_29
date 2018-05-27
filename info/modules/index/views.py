# 主页模块
from . import index_blue
from info import redis_store

@index_blue.route('/')
def index():
    '''主页'''

    # 操作redis
    redis_store.set('name','wjh')
    return 'index'