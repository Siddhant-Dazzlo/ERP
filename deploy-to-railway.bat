@echo off
echo 🚀 Trivanta Edge ERP - Railway Deployment Script
echo ================================================
echo.

echo 📋 Checking current status...
if not exist ".git" (
    echo ❌ Git repository not found. Initializing...
    git init
    echo ✅ Git initialized
) else (
    echo ✅ Git repository found
)

echo.
echo 🔄 Adding all files to git...
git add .

echo.
echo 💾 Committing changes...
git commit -m "Deploy to Railway: $(date /t) $(time /t)"

echo.
echo 📤 Pushing to GitHub...
git push

echo.
echo 🎉 Deployment initiated!
echo.
echo 📋 Next steps:
echo 1. Go to https://railway.app/dashboard
echo 2. Create new project
echo 3. Connect your GitHub repository
echo 4. Railway will auto-deploy your app
echo.
echo 🌐 Your app will be live at: https://your-app-name.railway.app
echo.
pause
