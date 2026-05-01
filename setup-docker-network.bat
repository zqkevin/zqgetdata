@echo off
chcp 65001 >nul
echo ========================================
echo   Docker 网络配置助手（1panel）
echo ========================================
echo.

echo [步骤 1] 检查 local_mysql 容器状态...
docker ps --filter "name=local_mysql" --format "{{.Names}}" | findstr "local_mysql" >nul
if errorlevel 1 (
    echo [错误] local_mysql 容器未运行！
    echo 请先启动 MySQL 容器：
    echo   docker start local_mysql
    echo.
    pause
    exit /b 1
)
echo [成功] local_mysql 容器正在运行
echo.

echo [步骤 2] 检查 1panel-network 网络...
docker network ls --format "{{.Name}}" | findstr "1panel-network" >nul
if errorlevel 1 (
    echo [错误] 1panel-network 网络不存在！
    echo 请确认 1panel 已正确安装并创建了网络
    echo.
    pause
    exit /b 1
)
echo [成功] 1panel-network 网络存在
echo.

echo [步骤 3] 检查 local_mysql 是否在 1panel-network 中...
docker network inspect 1panel-network --format="{{range .Containers}}{{.Name}} {{end}}" | findstr "local_mysql" >nul
if errorlevel 1 (
    echo [错误] local_mysql 不在 1panel-network 网络中！
    echo 请手动连接：
    echo   docker network connect 1panel-network local_mysql
    echo.
    pause
    exit /b 1
)
echo [成功] local_mysql 已在 1panel-network 中
echo.

echo [步骤 4] 显示网络信息...
echo.
echo === 1panel-network 中的容器 ===
docker network inspect 1panel-network --format="{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{chr 10}}{{end}}"
echo.

echo ========================================
echo   配置完成！
echo ========================================
echo.
echo zqgetdata 将自动加入 1panel-network
echo 现在可以启动 zqgetdata 容器：
echo   docker-compose up -d
echo.
echo 或者使用 docker-start.bat 选择选项 2
echo.
pause
