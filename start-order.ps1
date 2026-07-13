Write-Host "`n=== 订单服务启动 ===" -ForegroundColor Cyan

Write-Host "`n[1/2] 检查库存服务..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5002/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 库存服务已启动" -ForegroundColor Green
    } else {
        Write-Host "❌ 库存服务未启动" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ 库存服务未启动，请先启动库存服务" -ForegroundColor Red
    Write-Host "`n启动命令：" -ForegroundColor Yellow
    Write-Host "  .\start-inventory.ps1"
    exit 1
}

Write-Host "`n[2/2] 启动订单服务..." -ForegroundColor Yellow
Set-Location "order-service"
python -m uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload
