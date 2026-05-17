#!/bin/bash

# AI简历优化产品部署脚本
# 启动 Flask 服务并进行健康检查

# 项目根目录
PROJECT_ROOT="/home/joking/Dev/hermes/ai_resume_optimizer"
CODE_DIR="$PROJECT_ROOT/code"
VENV_DIR="$CODE_DIR/.venv"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/app.log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

echo "=== AI简历优化产品部署 ==="
echo "项目路径: $PROJECT_ROOT"
echo "代码目录: $CODE_DIR"
echo "虚拟环境: $VENV_DIR"
echo "日志文件: $LOG_FILE"
echo ""

# 激活虚拟环境
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "激活虚拟环境..."
    source "$VENV_DIR/bin/activate"
else
    echo "错误: 虚拟环境不存在于 $VENV_DIR"
    exit 1
fi

# 检查依赖是否已安装
echo "检查依赖..."
if ! pip list | grep -q "flask"; then
    echo "安装依赖..."
    pip install -r "$CODE_DIR/requirements.txt"
else
    echo "依赖已安装"
fi

# 启动 Flask 服务（后台运行）
echo "启动 Flask 服务 (端口: 5002)..."
cd "$CODE_DIR"
nohup python app.py > "$LOG_FILE" 2>&1 &
FLASK_PID=$!

echo "Flask 服务已启动 (PID: $FLASK_PID)"
echo "日志输出到: $LOG_FILE"
echo ""

# 健康检查 - 等待服务就绪
echo "进行健康检查..."
MAX_WAIT=30
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:5002/health > /dev/null; then
        echo "健康检查通过！服务已就绪"
        break
    fi
    
    echo -n "."
    sleep 1
    WAITED=$((WAITED + 1))
done

if [ $WAITED -eq $MAX_WAIT ]; then
    echo ""
    echo "警告: 健康检查超时 ($MAX_WAIT秒)，但服务可能仍在启动中"
    echo "请检查日志文件: $LOG_FILE"
else
    echo ""
fi

# 输出访问地址
echo ""
echo "=== 部署完成 ==="
echo "服务已启动，可通过以下地址访问:"
echo "API接口: http://0.0.0.0:5002"
echo "UI界面: http://0.0.0.0:5002/ui"
echo ""
echo "健康检查endpoint: http://0.0.0.0:5002/health"
echo "日志文件: $LOG_FILE"
echo ""
echo "注意:"
echo "- 服务在后台运行 (PID: $FLASK_PID)"
echo "- 要停止服务，请执行: kill $FLASK_PID"
echo "- 实时查看日志: tail -f $LOG_FILE"