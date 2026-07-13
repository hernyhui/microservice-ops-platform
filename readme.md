# 微服务应用使用说明书

## 项目概述

本项目是一个基于 Python FastAPI 的微服务应用，包含两个独立服务：

| 服务 | 端口 | 功能 |
|------|------|------|
| 订单服务 (Order Service) | 5001 | 创建订单、查询订单 |
| 库存服务 (Inventory Service) | 5002 | 查询库存、扣减库存 |

## 技术栈

- **框架**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.0
- **数据库**: MySQL（每个服务独立数据库）
- **缓存**: Redis（库存服务，已包含在项目中）
- **指标监控**: Prometheus Client

## 项目结构

```
微服务应用的全链路容器化与自动化运维平台/
├── .env                          # 环境变量配置
├── start-inventory.ps1           # 启动库存服务脚本
├── start-order.ps1               # 启动订单服务脚本
├── redis/                        # Redis 服务（已安装）
│   ├── redis-server.exe          # Redis 服务端
│   ├── redis-cli.exe             # Redis 命令行客户端
│   └── redis.windows.conf        # Redis 配置文件
├── order-service/                # 订单服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # 主入口，API路由
│   │   ├── config.py             # 配置管理
│   │   ├── database.py           # 数据库连接
│   │   ├── models.py             # SQLAlchemy模型
│   │   ├── schemas.py            # Pydantic数据模型
│   │   ├── inventory_client.py   # HTTP调用库存服务
│   │   └── metrics.py            # Prometheus指标
│   └── requirements.txt          # Python依赖
├── inventory-service/            # 库存服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # 主入口，API路由
│   │   ├── config.py             # 配置管理
│   │   ├── database.py           # 数据库连接
│   │   ├── models.py             # SQLAlchemy模型
│   │   ├── schemas.py            # Pydantic数据模型
│   │   ├── redis_client.py       # Redis缓存客户端
│   │   └── metrics.py            # Prometheus指标
│   ├── init_data.py              # 初始化测试数据
│   └── requirements.txt          # Python依赖
```

## 前置条件

### 1. 安装 Python
```powershell
# 要求 Python 3.8+
python --version
```

### 2. 安装 MySQL

确保本地已安装并启动 MySQL：
- 默认地址: `127.0.0.1:3306`
- 默认用户: `root`
- 默认密码: `123456`

### 3. Redis（已包含）
Redis 已预先安装在项目目录 `redis/` 下，无需额外安装：
- 默认地址: `127.0.0.1:6379`
- 配置文件: `redis/redis.windows.conf`

## 安装步骤

### 1. 创建数据库
```sql
CREATE DATABASE IF NOT EXISTS order_db DEFAULT CHARSET utf8mb4;
CREATE DATABASE IF NOT EXISTS inventory_db DEFAULT CHARSET utf8mb4;
```

### 2. 安装依赖
```powershell
# 安装订单服务依赖
cd order-service
pip install -r requirements.txt

# 安装库存服务依赖
cd ../inventory-service
pip install -r requirements.txt
```

### 3. 配置环境变量
编辑 `.env` 文件（通常已配置好）：
```env
ORDER_MYSQL_HOST=localhost
ORDER_MYSQL_PORT=3306
ORDER_MYSQL_USER=root
ORDER_MYSQL_PASSWORD=123456
ORDER_MYSQL_DB=order_db

INVENTORY_MYSQL_HOST=localhost
INVENTORY_MYSQL_PORT=3306
INVENTORY_MYSQL_USER=root
INVENTORY_MYSQL_PASSWORD=123456
INVENTORY_MYSQL_DB=inventory_db
```

### 4. 初始化库存数据

```powershell
cd inventory-service
python init_data.py
```

![image-20260707093833306](C:\Users\Lenovo\AppData\Roaming\Typora\typora-user-images\image-20260707093833306.png)

## 启动服务

### 步骤 1：启动 Redis（必须先启动）

打开 **终端1**：
```powershell
cd redis
.\redis-server.exe redis.windows.conf
```

验证 Redis 启动成功：
```powershell
# 打开另一个终端
cd redis
.\redis-cli.exe ping
# 预期输出: PONG
```

### 步骤 2：启动库存服务

打开 **终端2**：
```powershell
# 使用启动脚本
.\start-inventory.ps1

# 或手动启动
cd inventory-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 5002 --reload
```

### 步骤 3：启动订单服务

打开 **终端3**：
```powershell
# 使用启动脚本
.\start-order.ps1

# 或手动启动
cd order-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload
```

### 启动验证

```powershell
# 订单服务健康检查
powershell -command "Invoke-WebRequest -Uri "http://localhost:5001/health" -UseBasicParsing | Select-Object -ExpandProperty Content"

# 库存服务健康检查
powershell -command "Invoke-WebRequest -Uri "http://localhost:5002/health" -UseBasicParsing | Select-Object -ExpandProperty Content"
```

预期输出：
```json
{"status":"healthy","service":"order-service"}
{"status":"healthy","service":"inventory-service"}
```

## API 接口文档

### 订单服务 (http://localhost:5001)

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /metrics | Prometheus指标 |
| POST | /orders | 创建订单 |
| GET | /orders/{order_no} | 查询订单详情 |
| GET | /orders | 查询订单列表 |

#### 创建订单
```powershell
$body = '{"product_id": "PROD001", "product_name": "iPhone 15 Pro", "quantity": 2, "unit_price": 799900}'
Invoke-WebRequest -Uri "http://localhost:5001/orders" -Method POST -ContentType "application/json" -Body $body -UseBasicParsing | Select-Object -ExpandProperty Content
```

响应示例：
```json
{
  "id": 1,
  "order_no": "ORD93346DB1D44349E4",
  "product_id": "PROD001",
  "product_name": "iPhone 15 Pro",
  "quantity": 2,
  "total_amount": 1599800,
  "status": "paid",
  "created_at": "2026-07-06T12:59:33",
  "updated_at": "2026-07-06T12:59:33"
}
```

### 库存服务 (http://localhost:5002)

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /metrics | Prometheus指标 |
| GET | /inventory/{product_id} | 查询库存 |
| POST | /inventory | 创建库存记录 |
| PUT | /inventory/{product_id} | 更新库存 |
| POST | /inventory/deduct | 扣减库存 |

#### 查询库存
```powershell
Invoke-WebRequest -Uri "http://localhost:5002/inventory/PROD001" -UseBasicParsing | Select-Object -ExpandProperty Content
```

响应示例：
```json
{"product_id":"PROD001","product_name":"iPhone 15 Pro","stock":98,"id":1,"created_at":"2026-07-06T12:53:08","updated_at":"2026-07-06T12:59:33"}
```

#### 扣减库存
```powershell
$body = '{"product_id": "PROD001", "quantity": 2}'
Invoke-WebRequest -Uri "http://localhost:5002/inventory/deduct" -Method POST -ContentType "application/json" -Body $body -UseBasicParsing | Select-Object -ExpandProperty Content
```

## 测试流程

### 核心验证：创建订单后库存减少

1. **查询初始库存**
```powershell
Invoke-WebRequest -Uri "http://localhost:5002/inventory/PROD001" -UseBasicParsing | Select-Object -ExpandProperty Content
# 库存: 88
```

2. **创建订单**
```powershell
$body = '{"product_id": "PROD001", "product_name": "iPhone 15 Pro", "quantity": 3, "unit_price": 799900}'
Invoke-WebRequest -Uri "http://localhost:5001/orders" -Method POST -ContentType "application/json" -Body $body -UseBasicParsing | Select-Object -ExpandProperty Content
```

3. **验证库存减少**
```powershell
Invoke-WebRequest -Uri "http://localhost:5002/inventory/PROD001" -UseBasicParsing | Select-Object -ExpandProperty Content
# 库存: 95 (减少了3)
```

4. **验证 Redis 缓存同步**
```powershell
cd redis
.\redis-cli.exe get "inventory:stock:PROD001"
# 预期输出: 95
```

### 测试用例

| 测试项 | 步骤 | 预期结果 |
|--------|------|----------|
| Redis 启动 | `redis-cli ping` | 返回 PONG |
| 健康检查 | GET /health | 返回 200 |
| 指标端点 | GET /metrics | 返回 Prometheus 格式 |
| 创建订单 | POST /orders | 创建成功，订单号唯一 |
| 库存扣减 | 订单创建后查询库存 | 库存相应减少 |
| Redis 缓存 | 查询缓存键值 | 与数据库一致 |
| 库存不足 | 创建超库存订单 | 返回 400 错误 |

## Prometheus 指标

### 订单服务指标

| 指标名 | 类型 | 描述 |
|--------|------|------|
| order_requests_total | Counter | 请求总数 |
| order_request_duration_seconds | Histogram | 请求延迟 |
| order_create_total | Counter | 订单创建总数 |
| order_inventory_call_total | Counter | 调用库存服务次数 |

### 库存服务指标

| 指标名 | 类型 | 描述 |
|--------|------|------|
| inventory_requests_total | Counter | 请求总数 |
| inventory_request_duration_seconds | Histogram | 请求延迟 |
| inventory_deduct_total | Counter | 库存扣减总数 |
| inventory_query_total | Counter | 库存查询总数 |

## 配置说明

### 环境变量

**订单服务**（前缀 `ORDER_`）：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| ORDER_MYSQL_HOST | localhost | MySQL地址 |
| ORDER_MYSQL_PORT | 3306 | MySQL端口 |
| ORDER_MYSQL_USER | root | MySQL用户 |
| ORDER_MYSQL_PASSWORD | 123456 | MySQL密码 |
| ORDER_MYSQL_DB | order_db | 数据库名 |
| ORDER_SERVICE_PORT | 5001 | 服务端口 |

**库存服务**（前缀 `INVENTORY_`）：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| INVENTORY_MYSQL_HOST | localhost | MySQL地址 |
| INVENTORY_MYSQL_PORT | 3306 | MySQL端口 |
| INVENTORY_MYSQL_USER | root | MySQL用户 |
| INVENTORY_MYSQL_PASSWORD | 123456 | MySQL密码 |
| INVENTORY_MYSQL_DB | inventory_db | 数据库名 |
| INVENTORY_REDIS_HOST | 127.0.0.1 | Redis地址 |
| INVENTORY_REDIS_PORT | 6379 | Redis端口 |
| INVENTORY_SERVICE_PORT | 5002 | 服务端口 |

## 架构说明

### 服务间通信

```
订单服务 (5001)
    │
    ▼ HTTP POST
库存服务 (5002) /inventory/deduct
    │
    ├── 更新 MySQL (inventory_db)
    │
    └── 更新 Redis 缓存
```

### 库存查询流程

```
查询请求
    │
    ▼
查 Redis 缓存
    │
    ├── 命中 → 返回缓存数据
    │
    └── 未命中 → 查 MySQL → 更新 Redis → 返回数据
```

## 常见问题

### 1. Redis 连接失败
```powershell
# 确保 Redis 已启动
cd redis
.\redis-server.exe redis.windows.conf

# 验证连接
.\redis-cli.exe ping
```

### 2. 数据库连接失败
```powershell
# 确认 MySQL 服务已启动
netstat -ano | findstr "3306"

# 确认数据库已创建
mysql -u root -p123456 -e "SHOW DATABASES;"
```

### 3. 端口被占用
```powershell
# 查找占用端口的进程
netstat -ano | findstr "5001"
netstat -ano | findstr "5002"
netstat -ano | findstr "6379"

# 结束进程
taskkill /F /PID <进程ID>
```

### 4. 库存扣减失败
```powershell
# 检查库存是否足够
Invoke-WebRequest -Uri "http://localhost:5002/inventory/PROD001" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### 5. 查看 Redis 缓存
```powershell
cd redis
.\redis-cli.exe keys "*"              # 查看所有缓存键
.\redis-cli.exe get "inventory:stock:PROD001"  # 查看特定商品库存
```

## 停止服务

```powershell
# 停止 Redis（在 Redis 运行的终端按 Ctrl+C）

# 停止 Python 服务
taskkill /F /FI "IMAGENAME eq python.exe"
```

---

## 附录：测试数据

初始化脚本创建的测试商品：

| product_id | product_name | stock |
|------------|--------------|-------|
| PROD001 | iPhone 15 Pro | 100 |
| PROD002 | MacBook Pro 14 | 50 |
| PROD003 | AirPods Pro | 200 |
