Write-Host "`n=== 库存服务启动 ===" -ForegroundColor Cyan

Write-Host "`n[1/2] 检查 Redis 连接..." -ForegroundColor Yellow
try {
    Set-Location "redis"
    $result = .\redis-cli.exe ping 2>&1
    if ($result -eq "PONG") {
        Write-Host "✅ Redis 连接成功" -ForegroundColor Green
    } else {
        Write-Host "❌ Redis 未启动，请先启动 Redis" -ForegroundColor Red
        Write-Host "`n启动命令：" -ForegroundColor Yellow
        Write-Host "  cd redis"
        Write-Host "  .\redis-server.exe redis.windows.conf"
        exit 1
    }
} catch {
    Write-Host "❌ Redis 未启动或无法连接" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/2] 启动库存服务..." -ForegroundColor Yellow
Set-Location "inventory-service"
python -m uvicorn app.main:app --host 0.0.0.0 --port 5002 --reload
