#!/usr/bin/env bash
# 在阿里云服务器上把站点更新到 GitHub 上的最新版本，并重新生成 site/
set -euo pipefail

SRC="${BLOG_SRC:-/opt/blog/src}"
PY="${BLOG_PYTHON:-/opt/blog/venv/bin/python}"

cd "$SRC"

if [ -d .git ]; then
  echo "==> git fetch / pull"
  git fetch --all --prune
  git pull --ff-only
else
  echo "!! $SRC 不是 git 仓库，跳过 git pull（请手动同步源码）"
fi

echo "==> 构建静态站"
"$PY" build_blog.py --clean

echo "==> 完成：$(date '+%Y-%m-%d %H:%M:%S')"
