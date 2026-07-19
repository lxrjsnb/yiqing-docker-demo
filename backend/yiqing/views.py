"""
舆情系统演示接口
每个接口对应一个 Docker 编排的验证点
"""
import json
import redis
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

# 复用一个 Redis 客户端（专门做访问计数演示）
_redis_client = redis.Redis(
    host='redis',
    port=6379,
    db=2,
    decode_responses=True,
)


def hello(request):
    """健康检查：证明 Django 容器活着"""
    return JsonResponse({
        'status': 'ok',
        'service': 'yiqing-backend',
        'msg': 'Hello from Django in Docker!',
    })


def db_test(request):
    """测试 MySQL 连接：直接查询数据库当前时间"""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT NOW(), DATABASE(), VERSION()')
            row = cursor.fetchone()
        return JsonResponse({
            'status': 'ok',
            'db_time': str(row[0]),
            'db_name': row[1],
            'db_version': row[2],
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)}, status=500)


def redis_test(request):
    """
    测试 Redis 连接 + 演示持久化
    每访问一次，计数器 +1，重启 backend 容器后计数不丢（Redis 是独立容器 + Volume）
    """
    try:
        count = _redis_client.incr('visit_count')
        return JsonResponse({
            'status': 'ok',
            'visit_count': count,
            'msg': f'这是本接口第 {count} 次被访问，Redis 数据持久化在 Volume 里',
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)}, status=500)


def posts(request):
    """
    模拟舆情数据列表（静态假数据，演示前后端联调即可）
    真实系统这里是从 MySQL 查 Post 表
    """
    data = [
        {'id': 1, 'platform': '微博', 'author': '@科技日报',
         'content': '某品牌新机型发布会在京举行，现场反响热烈',
         'sentiment': '正面', 'likes': 1280, 'risk_level': '低'},
        {'id': 2, 'platform': '抖音', 'author': '@用户9527',
         'content': '刚买的新品用了三天就坏了，客服态度极差！',
         'sentiment': '负面', 'likes': 5600, 'risk_level': '高'},
        {'id': 3, 'platform': '知乎', 'author': '数码评测师',
         'content': '从硬件参数看，这款产品的性价比处于行业中游水平',
         'sentiment': '中性', 'likes': 890, 'risk_level': '中'},
        {'id': 4, 'platform': 'B站', 'author': '@UP主小王',
         'content': '深度评测视频已发，综合评分 7.5/10，欢迎三连',
         'sentiment': '中性', 'likes': 2300, 'risk_level': '低'},
    ]
    return JsonResponse({'status': 'ok', 'count': len(data), 'data': data})
