# filepath: export_v1_data.ps1
# MaxKB v1 数据导出脚本 (PowerShell版本)

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

Write-ColorOutput "=== MaxKB v1 数据导出脚本 ===" "Blue"
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

    # 复制迁移工具到v1容器
    Write-Step "复制迁移工具到v1容器..."
    docker cp . "${ContainerName}:/opt/maxkb/app/v1-to-v2-migrator"
    if ($LASTEXITCODE -ne 0) {
        throw "复制迁移工具失败"
    }
    Write-Success "迁移工具复制完成"

    # 在v1容器中导出数据
    Write-Step "在v1容器中导出数据..."
    docker exec -w /opt/maxkb/app/v1-to-v2-migrator $ContainerName python migrate.py export
    if ($LASTEXITCODE -ne 0) {
        throw "数据导出失败"
    }
    Write-Success "数据导出完成"

    # 复制数据到主机
    Write-Step "复制导出的数据到主机..."
    docker cp "${ContainerName}:/opt/maxkb/app/v1-to-v2-migrator/migrate.zip" "./migrate.zip"
    if ($LASTEXITCODE -ne 0) {
        throw "复制数据文件失败"
    }
    Write-Success "数据文件已保存到: ./migrate.zip"

    Write-Host
    Write-ColorOutput "[成功] v1数据导出完成!" "Green"
    Write-Info "导出文件: ./migrate.zip"
    Write-Warning "下一步: 请将migrate.zip和迁移工具复制到v2容器中进行导入"
    Write-Host
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
