@echo off
REM filepath: import_v2_data.bat
REM MaxKB v2 数据导入脚本 (Windows 批处理版本)

setlocal enabledelayedexpansion

echo === MaxKB v2 数据导入脚本 ===
echo.

REM 检查是否提供了容器名称参数
if "%1"=="" (
    echo [错误] 未提供容器名称
    echo [用法] %~nx0 ^<v2_container_name^>
    echo [示例] %~nx0 maxkb
    echo [提示] 使用 'docker ps' 查看当前运行的容器
    exit /b 1
)

set V2_CONTAINER=%1
echo [信息] 使用指定的容器: %V2_CONTAINER%
echo [确认] 目标容器: %V2_CONTAINER%
echo.

REM 检查容器是否存在且运行中
docker ps --format "{{.Names}}" | findstr /r "^%V2_CONTAINER%$" >nul
if !errorlevel! neq 0 (
    echo [错误] 容器 %V2_CONTAINER% 未运行或不存在
    echo [提示] 使用 'docker ps' 查看当前运行的容器
    exit /b 1
)

REM 检查迁移数据文件是否存在
if not exist ".\migrate.zip" (
    echo [错误] 迁移数据文件 .\migrate.zip 不存在
    echo [提示] 请先运行 export_v1_data.bat 导出v1数据
    exit /b 1
)

REM 复制迁移数据文件到v2容器
echo [步骤1] 复制迁移数据文件到v2容器...
docker cp . "%V2_CONTAINER%":/opt/maxkb-app/v1-to-v2-migrator
if !errorlevel! neq 0 (
    echo [错误] 复制迁移数据文件失败
    exit /b 1
)
echo [完成] 迁移数据文件复制完成

REM 在v2容器中导入数据
echo [步骤2] 在v2容器中导入数据...
docker exec -w /opt/maxkb-app/v1-to-v2-migrator "%V2_CONTAINER%" python migrate.py import
if !errorlevel! neq 0 (
    echo [错误] 数据导入失败
    exit /b 1
)
echo [完成] 数据导入完成

REM 清理v2容器中的临时文件
echo [步骤3] 清理临时文件...
docker exec "%V2_CONTAINER%" rm -rf /opt/maxkb-app/v1-to-v2-migrator/migrate.zip 2>nul
echo [完成] 临时文件清理完成

echo.
echo [成功] v1数据导入到v2完成!
echo [提示] 请重启v2容器以确保所有更改生效
echo.
echo 建议的重启命令:
echo   docker restart %V2_CONTAINER%
echo.

endlocal
