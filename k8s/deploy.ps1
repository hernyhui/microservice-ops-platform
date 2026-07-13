Write-Host "`n=== Kubernetes 一键部署脚本 ===" -ForegroundColor Cyan
Write-Host "日期: $(Get-Date)" -ForegroundColor Gray

$k8sPath = "E:\项目\微服务应用的全链路容器化与自动化运维平台\k8s"

Write-Host "`n[1/5] 检查 kubectl..." -ForegroundColor Yellow
try {
    kubectl version --client | Out-Null
    Write-Host "✅ kubectl 已安装" -ForegroundColor Green
} catch {
    Write-Host "❌ kubectl 未安装，请先安装 Kubernetes" -ForegroundColor Red
    Write-Host "   推荐安装 Docker Desktop 并启用 Kubernetes" -ForegroundColor Gray
    exit 1
}

Write-Host "`n[2/5] 检查 Kubernetes 集群..." -ForegroundColor Yellow
try {
    kubectl cluster-info | Out-Null
    Write-Host "✅ Kubernetes 集群已连接" -ForegroundColor Green
} catch {
    Write-Host "❌ 无法连接 Kubernetes 集群" -ForegroundColor Red
    Write-Host "   请检查 Docker Desktop 是否已启动并启用 Kubernetes" -ForegroundColor Gray
    exit 1
}

Write-Host "`n[3/5] 部署 Secret..." -ForegroundColor Yellow
kubectl apply -f "$k8sPath\secret.yaml"

Write-Host "`n[4/5] 部署 ConfigMap..." -ForegroundColor Yellow
kubectl apply -f "$k8sPath\order-configmap.yaml"
kubectl apply -f "$k8sPath\inventory-configmap.yaml"

Write-Host "`n[5/5] 部署 Deployment 和 Service..." -ForegroundColor Yellow
kubectl apply -f "$k8sPath\inventory-deployment.yaml"
kubectl apply -f "$k8sPath\inventory-service.yaml"
kubectl apply -f "$k8sPath\order-deployment.yaml"
kubectl apply -f "$k8sPath\order-service.yaml"

Write-Host "`n=== 部署完成 ===" -ForegroundColor Cyan
Write-Host "等待 Pod 启动..." -ForegroundColor Gray
Start-Sleep -Seconds 30

Write-Host "`n=== Pod 状态 ===" -ForegroundColor Cyan
kubectl get pods -l app in (order-service,inventory-service)

Write-Host "`n=== Service 状态 ===" -ForegroundColor Cyan
kubectl get svc order-service inventory-service

Write-Host "`n=== 测试命令 ===" -ForegroundColor Cyan
Write-Host "  # 查看 Pod 日志" -ForegroundColor Gray
Write-Host "  kubectl logs -l app=order-service" -ForegroundColor Gray
Write-Host "  kubectl logs -l app=inventory-service" -ForegroundColor Gray
Write-Host "" -ForegroundColor Gray
Write-Host "  # 端口转发测试" -ForegroundColor Gray
Write-Host "  kubectl port-forward svc/order-service 5001:5001" -ForegroundColor Gray
Write-Host "  curl http://localhost:5001/health" -ForegroundColor Gray
Write-Host "" -ForegroundColor Gray
Write-Host "  # 集群内互相调用" -ForegroundColor Gray
Write-Host "  kubectl exec -it <pod-name> -- curl http://inventory-service:5002/health" -ForegroundColor Gray
