# filepath: import_v2_data.ps1
# MaxKB v2 数据导入脚本 (PowerShell版本)

param(
    [Parameter(Mandatory=$true)]
    [string]$ContainerName
)

# 错误时立即停止
$ErrorActionPreference = "Stop"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "[步骤] $Message" "Magenta"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[完成] $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "[错误] $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "[信息] $Message" "Cyan"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[提示] $Message" "Yellow"
}

Write-ColorOutput "=== MaxKB v2 数据导入脚本 ===" "Blue"
Write-Host

Write-Info "使用指定的容器: $ContainerName"
Write-Info "目标容器: $ContainerName"
Write-Host

try {
    # 检查容器是否存在且运行中
    Write-Info "检查容器状态..."
    $containerExists = docker ps --format "{{.Names}}" | Where-Object { $_ -eq $ContainerName }
    if (-not $containerExists) {
        Write-Error "容器 $ContainerName 未运行或不存在"
        Write-Warning "使用 'docker ps' 查看当前运行的容器"
        exit 1
    }

    # 检查迁移数据文件是否存在
    Write-Info "检查迁移数据文件..."
    if (-not (Test-Path "./migrate.zip")) {
        Write-Error "迁移数据文件 ./migrate.zip 不存在"
        Write-Warning "请先运行 export_v1_data.ps1 导出v1数据"
        exit 1
    }

    # 复制迁移数据文件到v2容器
    Write-Step "复制迁移数据文件到v2容器..."
    docker cp . "${ContainerName}:/opt/maxkb-app/v1-to-v2-migrator"
    if ($LASTEXITCODE -ne 0) {
        throw "复制迁移数据文件失败"
    }
    Write-Success "迁移数据文件复制完成"

    # 在v2容器中导入数据
    Write-Step "在v2容器中导入数据..."
    docker exec -w /opt/maxkb-app/v1-to-v2-migrator $ContainerName python migrate.py import
    if ($LASTEXITCODE -ne 0) {
        throw "数据导入失败"
    }
    Write-Success "数据导入完成"

    # 清理v2容器中的临时文件
    Write-Step "清理临时文件..."
    docker exec $ContainerName rm -rf /opt/maxkb-app/v1-to-v2-migrator/migrate.zip 2>$null
    Write-Success "临时文件清理完成"

    Write-Host
    Write-ColorOutput "[成功] v1数据导入到v2完成!" "Green"
    Write-Warning "请重启v2容器以确保所有更改生效"
    Write-Host
    Write-Info "建议的重启命令:"
    Write-ColorOutput "  docker restart $ContainerName" "Blue"
    Write-Host
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
