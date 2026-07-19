# ============================================
# 前端 Dockerfile：最简版（用 CDN 引入 Vue3，免 npm 构建）
# 真实项目会做多阶段构建：node build → nginx 托管 dist/
# ============================================

FROM nginx:alpine

# 删掉 nginx 默认配置和默认页面
RUN rm /etc/nginx/conf.d/default.conf /usr/share/nginx/html/*

# 复制我们的配置和页面
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/

EXPOSE 80
