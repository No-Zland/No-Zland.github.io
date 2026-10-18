# 博客后端

FastAPI + SQLite，部署在阿里云 `/opt/blog`，Nginx 80 服务静态站，8001 仅监听本机。

## 环境变量 `/opt/blog/.env`

```text
BLOG_ROOT=/opt/blog
BLOG_PYTHON=/opt/blog/venv/bin/python
BLOG_ADMIN_PASSWORD=替换成强密码
BLOG_SECRET=替换成随机长字符串
```

`BLOG_ADMIN_PASSWORD` 是网页登录密码，`BLOG_SECRET` 用于签名会话 Cookie；两者都不要提交到仓库。

## 文件布局

```text
/opt/blog/
  venv/           Python 依赖
  src/            博客源码（build_blog.py、content/post、src）
  src/site/       Nginx 静态根目录
  app/            FastAPI 应用
  data/blog.db    SQLite
  .env
```

## 接口

- `GET /api/health`
- `GET /api/me`
- `POST /api/login` `{password}`
- `POST /api/logout`
- `POST /api/notes` `{title, section, category, body}`，写入后自动构建
- `GET /api/tasks` / `PUT /api/tasks` `{tasks: []}`，需要登录

## 部署

```bash
apt-get install -y nginx python3-venv
python3 -m venv /opt/blog/venv
/opt/blog/venv/bin/pip install -r /opt/blog/requirements.txt
cp /opt/blog/app/blog-api.service /etc/systemd/system/blog-api.service
cp /opt/blog/app/nginx-blog.conf /etc/nginx/sites-available/blog
ln -sf /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/blog
rm -f /etc/nginx/sites-enabled/default
systemctl daemon-reload
systemctl enable --now blog-api nginx
nginx -t && systemctl reload nginx
```
