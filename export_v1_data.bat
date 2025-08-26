@echo off
REM filepath: export_v1_data.bat
REM MaxKB v1 数据导出脚本 (Windows 批处理版本)

setlocal enabledelayedexpansion

echo === MaxKB v1 数据导出脚本 ===
echo.

REM 检查是否提供了容器名称参数
if "%1"=="" (
    echo [错误] 未提供容器名称
    echo [用法] %~nx0 ^<v1_container_name^>
    echo [示例] %~nx0 maxkb
    echo [提示] 使用 'docker ps' 查看当前运行的容器
    exit /b 1
)

set V1_CONTAINER=%1
echo [信息] 使用指定的容器: %V1_CONTAINER%
echo [确认] 目标容器: %V1_CONTAINER%
echo.

REM 检查容器是否存在且运行中
docker ps --format "{{.Names}}" | findstr /r "^%V1_CONTAINER%$" >nul
if !errorlevel! neq 0 (
    echo [错误] 容器 %V1_CONTAINER% 未运行或不存在
    echo [提示] 使用 'docker ps' 查看当前运行的容器
    exit /b 1
)

REM 复制迁移工具到v1容器
echo [步骤1] 复制迁移工具到v1容器...
docker cp . "%V1_CONTAINER%":/opt/maxkb/app/v1-to-v2-migrator
if !errorlevel! neq 0 (
    echo [错误] 复制迁移工具失败
    exit /b 1
)
echo [完成] 迁移工具复制完成

REM 在v1容器中导出数据
echo [步骤2] 在v1容器中导出数据...
docker exec -w /opt/maxkb/app/v1-to-v2-migrator "%V1_CONTAINER%" python migrate.py export
if !errorlevel! neq 0 (
    echo [错误] 数据导出失败
    exit /b 1
)
echo [完成] 数据导出完成

REM 复制数据到主机
echo [步骤3] 复制导出的数据到主机...
docker cp "%V1_CONTAINER%":/opt/maxkb/app/v1-to-v2-migrator/migrate.zip .\migrate.zip
if !errorlevel! neq 0 (
    echo [错误] 复制数据文件失败
    exit /b 1
)
echo [完成] 数据文件已保存到: .\migrate.zip

echo.
echo [成功] v1数据导出完成!
echo [文件] 导出文件: .\migrate.zip
echo [提示] 下一步: 请将migrate.zip和迁移工具复制到v2容器中进行导入
echo.

endlocal
