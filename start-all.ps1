Write-Host "`n=== 微服务一键启动脚本 ===" -ForegroundColor Cyan
Write-Host "日期: $(Get-Date)" -ForegroundColor Gray

$projectPath = "E:\项目\微服务应用的全链路容器化与自动化运维平台"
$redisPath = "$projectPath\redis"

Write-Host "`n[1/4] 检查 Docker Desktop..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "✅ Docker Desktop 已运行" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Docker Desktop 未运行，请手动启动 Docker Desktop" -ForegroundColor Yellow
    Write-Host "   路径: C:\Program Files\Docker\Docker\Docker Desktop.exe" -ForegroundColor Gray
    Write-Host "   等待 15 秒..." -ForegroundColor Gray
    Start-Sleep -Seconds 15
}

Write-Host "`n[2/4] 启动 Redis..." -ForegroundColor Yellow
cd $redisPath
if (-not (Test-Path "redis-server.exe")) {
    Write-Host "❌ Redis 未找到: $redisPath" -ForegroundColor Red
    Write-Host "   请确认 Redis 已解压到该目录" -ForegroundColor Gray
    exit 1
}

$redisProcess = Get-Process redis-server -ErrorAction SilentlyContinue
if ($redisProcess) {
    Write-Host "✅ Redis 已在运行 (PID: $($redisProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "启动 Redis 服务..." -ForegroundColor Gray
    Start-Process -FilePath ".\redis-server.exe" -ArgumentList "redis.windows.conf" -NoNewWindow
    Start-Sleep -Seconds 3
    
    try {
        $pingResult = .\redis-cli.exe ping
        if ($pingResult -eq "PONG") {
            Write-Host "✅ Redis 启动成功" -ForegroundColor Green
        } else {
            Write-Host "❌ Redis 启动失败" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Redis 连接失败: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n[3/4] 检查 MySQL..." -ForegroundColor Yellow
try {
    mysql -u root -p123456 -e "SELECT 1" | Out-Null
    Write-Host "✅ MySQL 连接成功" -ForegroundColor Green
} catch {
    Write-Host "❌ MySQL 未启动或连接失败" -ForegroundColor Red
    Write-Host "   请检查 MySQL 服务是否已启动" -ForegroundColor Gray
    exit 1
}

Write-Host "`n[4/4] 启动微服务容器..." -ForegroundColor Yellow

Write-Host "创建 Docker 网络..." -ForegroundColor Gray
docker network create microservice-network 2>$null | Out-Null

Write-Host "删除旧容器..." -ForegroundColor Gray
docker rm -f order-service inventory-service 2>$null | Out-Null

Write-Host "启动库存服务..." -ForegroundColor Gray
docker run -d --name inventory-service --network microservice-network -p 5002:5002 `
  -e INVENTORY_MYSQL_HOST=host.docker.internal `
  -e INVENTORY_MYSQL_PASSWORD=123456 `
  -e INVENTORY_REDIS_HOST=host.docker.internal `
  inventory-service:1.0

Start-Sleep -Seconds 5

Write-Host "启动订单服务..." -ForegroundColor Gray
docker run -d --name order-service --network microservice-network -p 5001:5001 `
  -e ORDER_MYSQL_HOST=host.docker.internal `
  -e ORDER_MYSQL_PASSWORD=123456 `
  -e ORDER_INVENTORY_SERVICE_URL=http://inventory-service:5002 `
  order-service:1.0

Start-Sleep -Seconds 5

Write-Host "`n=== 服务状态检查 ===" -ForegroundColor Cyan
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n=== 健康检查 ===" -ForegroundColor Cyan
try {
    $orderHealth = Invoke-WebRequest -Uri "http://localhost:5001/health" -UseBasicParsing -TimeoutSec 5 | Select-Object -ExpandProperty Content
    Write-Host "订单服务: $orderHealth" -ForegroundColor Green
} catch {
    Write-Host "订单服务: ❌ 未响应" -ForegroundColor Red
}

try {
    $inventoryHealth = Invoke-WebRequest -Uri "http://localhost:5002/health" -UseBasicParsing -TimeoutSec 5 | Select-Object -ExpandProperty Content
    Write-Host "库存服务: $inventoryHealth" -ForegroundColor Green
} catch {
    Write-Host "库存服务: ❌ 未响应" -ForegroundColor Red
}

Write-Host "`n=== 启动完成 ===" -ForegroundColor Cyan
Write-Host "测试命令:" -ForegroundColor Gray
Write-Host "  curl http://localhost:5001/health" -ForegroundColor Gray
Write-Host "  curl http://localhost:5002/health" -ForegroundColor Gray
Write-Host "  curl -X POST http://localhost:5001/orders -H 'Content-Type: application/json' -d '{\"product_id\": \"PROD001\", \"quantity\": 1}'" -ForegroundColor Gray
