@echo off
chcp 65001 >nul
echo ========================================
echo   Soccer Data API 启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查虚拟环境...
if not exist "..\.venv\Scripts\activate.bat" (
    echo 错误: 未找到虚拟环境，请先在项目根目录运行: python -m venv .venv
    pause
    exit /b 1
)

echo [2/3] 激活虚拟环境...
call ..\.venv\Scripts\activate.bat

echo [3/3] 启动 API 服务...
echo.
echo API 文档地址: http://localhost:8000/docs
echo Swagger UI: http://localhost:8000/docs
echo ReDoc: http://localhost:8000/redoc
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python main.py

pause
