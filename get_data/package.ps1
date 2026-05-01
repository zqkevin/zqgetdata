# ============================================
# 项目打包脚本（PowerShell）
# 用于清理临时文件并打包项目
# ============================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  体育彩票数据采集系统 - 打包脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 设置项目名称
$PROJECT_NAME = "zqgetdata"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$PACKAGE_NAME = "${PROJECT_NAME}_${TIMESTAMP}.zip"

Write-Host "📦 开始打包项目..." -ForegroundColor Green
Write-Host ""

# 1. 清理不必要的文件
Write-Host "🧹 清理不必要的文件..." -ForegroundColor Yellow

# 删除 Python 缓存
if (Test-Path "__pycache__") {
    Remove-Item -Recurse -Force "__pycache__"
    Write-Host "   ✅ 删除 __pycache__"
}

Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Write-Host "   ✅ 删除所有 __pycache__ 目录"

# 删除 .pyc 文件
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
Write-Host "   ✅ 删除 *.pyc 文件"

# 删除虚拟环境
if (Test-Path ".venv") {
    Remove-Item -Recurse -Force ".venv"
    Write-Host "   ✅ 删除 .venv 虚拟环境"
}

# 删除日志文件（保留目录结构）
Get-ChildItem -Path "app\log" -Recurse -File -Filter "*.log" | Remove-Item -Force
Write-Host "   ✅ 清理日志文件"

# 删除 temp 目录中的临时文件（保留目录）
if (Test-Path "temp") {
    Get-ChildItem -Path "temp" -File | Remove-Item -Force
    Write-Host "   ✅ 清理 temp 目录中的文件"
}

# 删除测试覆盖率文件
if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }

Write-Host ""

# 2. 创建排除列表
Write-Host "📝 创建打包排除列表..." -ForegroundColor Yellow

$EXCLUDE_DIRS = @(
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "__pycache__",
    "node_modules",
    "htmlcov",
    ".pytest_cache"
)

$EXCLUDE_FILES = @(
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "Thumbs.db",
    "*.log",
    ".env",
    "docker-compose.override.yml"
)

Write-Host "   ✅ 排除列表已准备"
Write-Host ""

# 3. 打包项目
Write-Host "🗜️  正在压缩项目..." -ForegroundColor Yellow

# 获取项目根目录
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

# 使用 Compress-Archive 打包
try {
    # 获取所有需要打包的文件
    $FILES_TO_COMPRESS = Get-ChildItem -Path $PROJECT_ROOT -Recurse | Where-Object {
        $item = $_
        $shouldExclude = $false
        
        # 检查是否在排除目录中
        foreach ($dir in $EXCLUDE_DIRS) {
            if ($item.FullName -like "*\$dir\*" -or $item.FullName -like "*\$dir") {
                $shouldExclude = $true
                break
            }
        }
        
        # 检查是否是排除文件
        if (-not $shouldExclude) {
            foreach ($pattern in $EXCLUDE_FILES) {
                if ($item.Name -like $pattern) {
                    $shouldExclude = $true
                    break
                }
            }
        }
        
        -not $shouldExclude
    }
    
    # 创建压缩包
    $FILES_TO_COMPRESS | Compress-Archive -DestinationPath $PACKAGE_NAME -Force
    
    Write-Host "   ✅ 打包完成: $PACKAGE_NAME" -ForegroundColor Green
} catch {
    Write-Host "   ❌ 打包失败: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 4. 显示打包信息
$FILE_SIZE = (Get-Item $PACKAGE_NAME).Length / 1MB
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ✅ 打包成功！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📦 文件名: $PACKAGE_NAME" -ForegroundColor White
Write-Host "📊 大小: $([math]::Round($FILE_SIZE, 2)) MB" -ForegroundColor White
Write-Host "📁 位置: $(Join-Path $PROJECT_ROOT $PACKAGE_NAME)" -ForegroundColor White
Write-Host ""
Write-Host "🚀 部署步骤:" -ForegroundColor Yellow
Write-Host "   1. 将 $PACKAGE_NAME 上传到服务器" -ForegroundColor White
Write-Host "   2. 解压: unzip $PACKAGE_NAME" -ForegroundColor White
Write-Host "   3. 进入目录: cd $PROJECT_NAME" -ForegroundColor White
Write-Host "   4. 修改密码: 编辑 docker-compose.yml" -ForegroundColor White
Write-Host "   5. 启动服务: chmod +x deploy.sh && ./deploy.sh" -ForegroundColor White
Write-Host ""
