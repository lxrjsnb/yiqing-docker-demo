# ============================================
# 舆情系统后端 Dockerfile（带详细注释，方便面试讲解）
# ============================================

# 1. 基础镜像：Python 3.11 精简版（体积小、够用）
FROM python:3.11-slim

# 2. 设置环境变量：
#    - PYTHONUNBUFFERED=1 让 print 实时输出到 docker logs（不缓冲）
#    - PYTHONDONTWRITEBYTECODE=1 不生成 .pyc，镜像更干净
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. 装 mysqlclient 需要的系统依赖
#    这一步踩过坑：不装 gcc 和 default-libmysqlclient-dev，pip 装 mysqlclient 会报错
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/*

# 4. 设置工作目录
WORKDIR /app

# 5. 先单独复制 requirements.txt（利用 Docker 缓存层）
#    好处：代码改动时不重新装依赖，build 快很多
COPY requirements.txt /app/

# 6. 装依赖（用清华源，国内/Codespaces 都更快）
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 7. 复制项目代码
COPY . /app/

# 8. 暴露 Django 端口（仅声明，真正映射在 compose 里做）
EXPOSE 8000

# 9. 启动命令：等 MySQL 起来 → migrate → runserver
#    entrypoint.sh 比 CMD 更适合做"启动前准备"
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
