# 🚀 Trivanta Edge ERP - Railway Deployment Script (PowerShell)
Write-Host "🚀 Trivanta Edge ERP - Railway Deployment Script" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

Write-Host "📋 Checking current status..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    Write-Host "❌ Git repository not found. Initializing..." -ForegroundColor Red
    git init
    Write-Host "✅ Git initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository found" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔄 Adding all files to git..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
git commit -m "Deploy to Railway: $timestamp"

Write-Host ""
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
git push

Write-Host ""
Write-Host "🎉 Deployment initiated!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to https://railway.app/dashboard" -ForegroundColor White
Write-Host "2. Create new project" -ForegroundColor White
Write-Host "3. Connect your GitHub repository" -ForegroundColor White
Write-Host "4. Railway will auto-deploy your app" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Your app will be live at: https://your-app-name.railway.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
