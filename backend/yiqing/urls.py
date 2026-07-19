"""
yiqing URL Configuration
4 个测试接口：
  /api/hello/    健康检查
  /api/db/       测试 MySQL 连接
  /api/redis/    测试 Redis 连接（带访问计数）
  /api/posts/    模拟舆情数据列表
"""
from django.urls import path
from . import views

urlpatterns = [
    path('api/hello/', views.hello),
    path('api/db/', views.db_test),
    path('api/redis/', views.redis_test),
    path('api/posts/', views.posts),
]
