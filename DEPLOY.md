# AI简历优化产品部署说明

## 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Linux (本部署脚本针对 Arch Linux)
- **磁盘空间**: 至少 500MB 可用空间

## 项目结构

```
ai_resume_optimizer/
├── code/
│   ├── app.py              # Flask 主应用
│   ├── requirements.txt    # Python 依赖
│   ├── .env                # 环境变量配置
│   ├── .venv/              # Python 虚拟环境
│   ├── frontend/           # 前端文件
│   └── llm_client.py       # LLM 客户端
├── logs/                   # 日志目录（自动创建）
├── deploy.sh               # 一键部署脚本
└── DEPLOY.md               # 本文档
```

## 部署步骤

### 1. 检查环境

```bash
# 确认 Python 版本
python --version

# 确认项目目录
cd /home/joking/Dev/hermes/ai_resume_optimizer
```

### 2. 创建并激活虚拟环境（如果不存在）

```bash
cd /home/joking/Dev/hermes/ai_resume_optimizer/code
python -m venv .venv
source .venv/bin/activate
```

### 3. 配置环境变量

编辑 `code/.env` 文件，确保包含以下配置项：

```bash
# LLM API 配置
LLM_API_BASE=http://127.0.0.1:20128/v1
LLM_API_KEY=sk_9router
LLM_MODEL=local
```

| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| `LLM_API_BASE` | LLM API 服务地址 | `http://127.0.0.1:20128/v1` |
| `LLM_API_KEY` | API 密钥 | `sk_9router` |
| `LLM_MODEL` | 模型名称 | `local` |

### 4. 安装依赖

```bash
cd /home/joking/Dev/hermes/ai_resume_optimizer/code
pip install -r requirements.txt
```

**主要依赖说明**：
| 包名 | 用途 |
|------|------|
| flask | Web 框架 |
| flask-cors | 跨域支持 |
| langchain | LLM 编排 |
| langgraph | 流程图编排 |
| pdfplumber | PDF 解析 |
| python-dotenv | 环境变量加载 |

### 5. 一键部署（推荐）

项目根目录已包含 `deploy.sh` 脚本，可一键启动服务：

```bash
chmod +x /home/joking/Dev/hermes/ai_resume_optimizer/deploy.sh
/home/joking/Dev/hermes/ai_resume_optimizer/deploy.sh
```

脚本功能：
- 自动创建日志目录
- 激活虚拟环境
- 启动 Flask 服务（后台运行）
- 自动进行健康检查
- 输出访问地址

### 6. 手动启动（可选）

如果不想使用脚本，可手动执行：

```bash
cd /home/joking/Dev/hermes/ai_resume_optimizer/code
source .venv/bin/activate
nohup python app.py > ../logs/app.log 2>&1 &
```

## 访问方式

部署成功后，通过以下地址访问服务：

| 服务 | 地址 | 说明 |
|------|------|------|
| API 接口 | http://0.0.0.0:5002 | 后端 REST API |
| UI 界面 | http://0.0.0.0:5002/ui | Web 前端界面 |
| 健康检查 | http://0.0.0.0:5002/health | 服务状态检查 |

### 本机访问

```bash
# 使用 curl 测试
curl http://localhost:5002/health

# 使用浏览器访问
firefox http://localhost:5002/ui
```

### 局域网访问

将 `0.0.0.0` 替换为服务器 IP：

```bash
# 查询本机 IP
hostname -I

# 访问示例
http://192.168.1.100:5002/ui
```

## 服务管理

### 查看服务状态

```bash
# 检查进程是否运行
ps aux | grep "python app.py" | grep -v grep

# 健康检查
curl http://localhost:5002/health
```

### 查看日志

```bash
# 实时查看日志
tail -f /home/joking/Dev/hermes/ai_resume_optimizer/logs/app.log

# 查看完整日志
cat /home/joking/Dev/hermes/ai_resume_optimizer/logs/app.log
```

### 停止服务

```bash
# 查找进程 PID
ps aux | grep "python app.py"

# 停止服务
kill <PID>

# 或强制停止
pkill -f "python app.py"
```

### 重启服务

```bash
# 停止现有服务
pkill -f "python app.py"

# 重新部署
./deploy.sh
```

## 内网穿透（可选）

当前环境未安装 ngrok 或 frp。如需远程访问，可选以下方案：

### 方案一：ngrok

```bash
# 安装 ngrok（Linux）
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
# ... (参考 ngrok 官方安装文档)

# 启动穿透
ngrok http 5002
```

### 方案二：frp

```bash
# 配置 frpc.ini
[common]
server_addr = <frp服务器地址>
server_port = 7000

[flask]
type = tcp
local_ip = 127.0.0.1
local_port = 5002
remote_port = 5002

# 启动
frpc -c frpc.ini
```

## 常见问题

### 1. 端口被占用

```bash
# 查看端口占用
lsof -i :5002

# 停止占用进程或修改端口
```

### 2. 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

### 3. 健康检查失败

```bash
# 查看日志排查错误
cat /home/joking/Dev/hermes/ai_resume_optimizer/logs/app.log

# 常见问题：
# - LLM API 无法连接 -> 检查 .env 中的 LLM_API_BASE
# - 端口被占用 -> 使用其他端口或停止冲突进程
```

## 安全建议

1. **生产环境**：不要将 .env 文件提交到版本控制
2. **API 密钥**：使用环境变量或密钥管理服务存储敏感信息
3. **网络访问**：生产环境建议配置防火墙，限制访问来源

---

部署文档版本: 1.0.0  
更新日期: 2026-05-17