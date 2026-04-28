@echo off
chcp 65001 >nul
echo ========================================
echo   体育彩票数据采集系统 - Docker 部署
echo ========================================
echo.

:menu
echo 请选择操作：
echo.
echo 1. 构建并启动容器（首次运行）
echo 2. 启动容器（后台运行）
echo 3. 停止容器
echo 4. 重启容器
echo 5. 查看日志
echo 6. 进入容器
echo 7. 查看容器状态
echo 8. 清理未使用的资源
echo 9. 初始化数据库
echo 0. 退出
echo.
set /p choice=请输入选项 (0-9): 

if "%choice%"=="1" goto build_and_start
if "%choice%"=="2" goto start
if "%choice%"=="3" goto stop
if "%choice%"=="4" goto restart
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto exec
if "%choice%"=="7" goto status
if "%choice%"=="8" goto clean
if "%choice%"=="9" goto init_db
if "%choice%"=="0" goto end
goto menu

:build_and_start
echo.
echo [信息] 正在构建并启动容器...
docker-compose up --build
goto menu

:start
echo.
echo [信息] 正在后台启动容器...
docker-compose up -d
echo [成功] 容器已启动！
echo.
echo 提示：使用 "docker-compose logs -f" 查看实时日志
goto menu

:stop
echo.
echo [信息] 正在停止容器...
docker-compose down
echo [成功] 容器已停止
goto menu

:restart
echo.
echo [信息] 正在重启容器...
docker-compose restart
echo [成功] 容器已重启
goto menu

:logs
echo.
echo [信息] 显示最近 100 行日志（按 Ctrl+C 退出）
docker-compose logs --tail=100 -f
goto menu

:exec
echo.
echo [信息] 进入容器内部...
docker-compose exec zqgetdata bash
goto menu

:status
echo.
echo [信息] 容器状态：
docker-compose ps
echo.
echo [信息] 资源使用情况：
docker stats --no-stream zqgetdata_collector
goto menu

:clean
echo.
echo [警告] 这将删除所有未使用的镜像、容器和网络
set /p confirm=确认执行？(y/n): 
if /i "%confirm%"=="y" (
    docker system prune -a
    echo [成功] 清理完成
) else (
    echo [取消] 操作已取消
)
goto menu

:init_db
echo.
echo [信息] 正在初始化数据库...
docker-compose exec zqgetdata python init_db.py
echo [完成] 数据库初始化完成
goto menu

:end
echo.
echo 感谢使用！再见！
exit /b 0
