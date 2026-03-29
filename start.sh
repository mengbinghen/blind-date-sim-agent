#!/bin/bash
# AI相亲模拟Agent 启动脚本

cd "$(dirname "$0")/backend"

# 启动服务
echo "正在启动 AI相亲模拟Agent..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
