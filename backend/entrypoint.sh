#!/bin/sh
# ============================================
# 后端容器启动脚本
# 解决经典问题：backend 比 MySQL 先起来，导致 migrate 失败
# 思路：循环 ping MySQL，直到能连上才继续
# ============================================

echo "==> 等待 MySQL 就绪..."
until python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('db', 3306))
    s.close()
    exit(0)
except Exception:
    exit(1)
"; do
    echo "  MySQL 还没起来，5 秒后重试..."
    sleep 5
done
echo "==> MySQL 已就绪"

# 执行 Django 数据库迁移
echo "==> 执行 migrate..."
python manage.py migrate --noinput

# 执行传入的 CMD（即 runserver）
echo "==> 启动 Django 开发服务器..."
exec "$@"
