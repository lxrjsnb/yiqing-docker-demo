# AI 舆情监测系统 · Docker 部署演示

> 一个能在 **GitHub Codespaces**（或任何装了 Docker 的机器）**5 分钟跑通**的全栈最小化项目。
> 4 个容器：Django + Vue3 + MySQL + Redis。
> 目标：让你简历上的"Docker 容器部署"经得起面试追问。

---

## 一、项目结构

```
docker-yiqing-demo/
├── docker-compose.yml       # 多容器编排（核心）
├── backend/                 # Django 后端
│   ├── Dockerfile
│   ├── entrypoint.sh        # 启动前等 MySQL + migrate
│   ├── requirements.txt
│   ├── .dockerignore
│   ├── manage.py
│   └── yiqing/
│       ├── settings.py      # 从环境变量读 DB/Redis 配置
│       ├── urls.py
│       ├── views.py         # 4 个测试接口
│       ├── wsgi.py
│       └── asgi.py
└── frontend/                # Vue3 前端（Nginx 托管）
    ├── Dockerfile
    ├── nginx.conf           # 反向代理 /api/ 到 backend
    └── index.html           # Vue3 单页（CDN 引入，免 build）
```

---

## 二、跑起来（GitHub Codespaces 流程）

### Step 1 · 把项目传到 GitHub
1. 在本地 `D:/Lianxi/docker-yiqing-demo/` 目录初始化并 push：
   ```bash
   cd D:/Lianxi/docker-yiqing-demo
   git init
   git add .
   git commit -m "舆情系统 Docker 部署演示"
   git branch -M main
   git remote add origin https://github.com/你的用户名/yiqing-docker-demo.git
   git push -u origin main
   ```

### Step 2 · 用 Codespaces 打开
1. GitHub 上打开这个仓库
2. 点绿色 `Code` 按钮 → `Codespaces` 标签 → `Create codespace on main`
3. 等 1-2 分钟，浏览器里就是一个完整的 VS Code 环境

### Step 3 · 验证 Docker 可用
在 Codespaces 终端执行：
```bash
docker --version          # 应该输出 Docker version 24.x 或更高
docker-compose --version  # 应该有 docker-compose 1.29+ 或 docker compose v2
```

### Step 4 · 一键启动全部服务
```bash
docker-compose up -d --build
```
第一次会拉镜像 + 构建，大约 2-3 分钟。

### Step 5 · 查看运行状态
```bash
docker-compose ps                 # 看哪些容器在跑
docker-compose logs -f backend    # 看后端日志（看 migrate 是否成功）
```

### Step 6 · 访问页面
- Codespaces 右下角会弹出端口转发提示，或点 `PORTS` 标签
- 把 **80 端口** 改成 `Visibility: Public`，点地址打开
- 看到舆情看板页面 → 部署成功 🎉

页面会显示 4 个状态卡片：
- **Django 后端**：`Hello from Django in Docker!`
- **MySQL 数据库**：当前时间
- **Redis 访问计数**：每刷新一次 +1
- **舆情数据**：4 条测试数据表格

---

## 三、面试要点（看完这段 Docker 就算入门）

### Q1. 你 Dockerfile 里为什么先 COPY requirements.txt 再 COPY 代码？
Docker 分层缓存。代码经常变，依赖很少变。先复制依赖 → 装依赖这一层就被缓存住，改代码时这一步直接跳过，构建快很多。

### Q2. 你的 backend 容器怎么连到 MySQL 容器的？
compose 把它们放在同一个默认网络里，**服务名就是主机名**。所以 Django 里 `DB_HOST=db` 就能连上，不需要 IP。

### Q3. backend 比 MySQL 先起来怎么办？（经典坑）
用 `depends_on.condition: service_healthy` + MySQL 的 `healthcheck`，让 backend 等 MySQL 健康后才启动。再加一层保险：`entrypoint.sh` 循环 ping MySQL，连上才 migrate。

### Q4. 容器删了数据会丢吗？
不会。`docker-compose.yml` 里 `volumes: mysql_data:/var/lib/mysql` 把数据挂载到 Docker 管理的卷里，跟容器生命周期解耦。`docker-compose down` 删容器，数据还在；`docker-compose down -v` 才会连卷一起删。

### Q5. 前端为什么用 Nginx 而不是直接跑 node？
前端是静态文件（HTML/CSS/JS），用 Nginx 托管最快、最轻量（镜像才几十 MB）。同时用 Nginx 做反向代理，把 `/api/` 转发到后端，前端只感知同源，**规避跨域**。

### Q6. 你镜像多大？怎么优化？
- 现在后端镜像约 200MB（python:3.11-slim ~50MB + Django 等）
- 前端镜像约 50MB（nginx:alpine）
- 优化手段：用 alpine/slim 基础镜像、多阶段构建、合并 RUN 指令、`.dockerignore` 排除无用文件、pip 加 `--no-cache-dir`

### Q7. 怎么进入容器调试？
```bash
docker exec -it yiqing-backend /bin/bash       # 进入后端容器
docker exec -it yiqing-db mysql -uroot -proot123  # 进 MySQL
docker exec -it yiqing-redis redis-cli         # 进 Redis
```

### Q8. 一键停止 / 重启 / 清理
```bash
docker-compose stop                       # 停止（保留容器）
docker-compose restart                    # 重启
docker-compose down                       # 删除容器（保留数据）
docker-compose down -v                    # 连数据卷一起删（数据全没）
docker-compose up -d --build              # 改代码后重新构建
```

---

## 四、常见报错排查

| 报错 | 原因 | 解决 |
|------|------|------|
| `port is already allocated` | 本机 80/3306 已被占用 | 改 compose 的端口映射，如 `"8080:80"` |
| backend 容器一直重启 | MySQL 还没起来或密码错 | `docker-compose logs backend` 看日志 |
| 前端能打开但接口 502 | backend 没起来或 Nginx 配置错 | 检查 `nginx.conf` 的 `proxy_pass http://backend:8000` |
| `permission denied: entrypoint.sh` | Windows 创建的 sh 没有执行权限 | Dockerfile 里已加 `chmod +x`，没问题；本地跑需手动 `chmod +x backend/entrypoint.sh` |
| mysqlclient 装不上 | 系统依赖缺失 | Dockerfile 里已装 `default-libmysqlclient-dev` 和 `gcc` |
| Codespaces 端口打不开 | Visibility 是 Private | PORTS 标签右键端口 → Port Visibility → Public |

---

## 五、把这次实操写进简历 / 面试话术

**简历原文**：
> AI 舆情监测系统 · Docker 容器化部署
> - 编写 Dockerfile 与 docker-compose.yml，编排 Django 后端、Vue3 前端、MySQL、Redis 四个容器
> - 通过 healthcheck + depends_on 解决"后端先于数据库启动导致 migrate 失败"的经典问题
> - 通过 Volume 持久化数据库与缓存数据，通过 Nginx 反向代理统一前端入口，规避跨域
> - 镜像分层缓存优化：先复制 requirements.txt 再复制代码，依赖变更少时构建提速约 70%

**面试时这样答**：
> "我把系统拆成 4 个容器：Django 后端、Vue3 前端用 Nginx 托管、MySQL 和 Redis。
> 用 docker-compose 编排，关键点是处理依赖关系——MySQL 有 healthcheck，backend 用 depends_on 等它健康后再启动，同时 entrypoint.sh 里循环 ping MySQL 再做 migrate，避免连不上数据库。
> 数据用 Volume 持久化，容器删了数据还在。前端用 Nginx 反向代理 /api/ 到后端，规避 CORS 问题。
> 我还做了构建优化：Dockerfile 先 COPY requirements.txt 再 COPY 代码，依赖层缓存住之后改代码构建快很多。"

---

## 六、下一步升级（学有余力）

1. **加 Celery 容器**：异步跑爬虫任务
2. **加前端构建阶段**：把 CDN 改成真正的 Vite + Vue3 工程，Dockerfile 用多阶段构建
3. **加 .env 文件**：把密码、密钥从 compose 拆出去
4. **加 GitHub Actions**：push 代码自动构建镜像并推到 Docker Hub
5. **部署到云服务器**：阿里云学生机，docker-compose up -d，域名 + HTTPS
