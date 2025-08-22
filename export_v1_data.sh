#!/bin/bash
# filepath: export_v1_data.sh

set -e  # 遇到错误立即退出

echo "=== MaxKB v1 数据导出脚本 ==="
echo

# 检查是否提供了容器名称参数
if [ -z "$1" ]; then
    echo "[错误] 未提供容器名称"
    echo "[用法] $0 <v1_container_name>"
    echo "[示例] $0 maxkb"
    echo "[提示] 使用 'docker ps' 查看当前运行的容器"
    exit 1
fi

V1_CONTAINER="$1"
echo "[信息] 使用指定的容器: $V1_CONTAINER"
echo "[确认] 目标容器: $V1_CONTAINER"
echo

# 检查容器是否存在且运行中
if ! docker ps --format "{{.Names}}" | grep -q "^$V1_CONTAINER$"; then
    echo "[错误] 容器 $V1_CONTAINER 未运行或不存在"
    echo "[提示] 使用 'docker ps' 查看当前运行的容器"
    exit 1
fi

# 复制迁移工具到v1容器
echo "[步骤1] 复制迁移工具到v1容器..."
if ! docker cp . "$V1_CONTAINER":/opt/maxkb/app/v1-to-v2-migrator; then
    echo "[错误] 复制迁移工具失败"
    exit 1
fi
echo "[完成] 迁移工具复制完成"

# 在v1容器中导出数据
echo "[步骤2] 在v1容器中导出数据..."
if ! docker exec -w /opt/maxkb/app/v1-to-v2-migrator "$V1_CONTAINER" python migrate.py export; then
    echo "[错误] 数据导出失败"
    exit 1
fi
echo "[完成] 数据导出完成"

# 复制数据到主机
echo "[步骤3] 复制导出的数据到主机..."
if ! docker cp "$V1_CONTAINER":/opt/maxkb/app/v1-to-v2-migrator/migrate.zip ./migrate.zip; then
    echo "[错误] 复制数据文件失败"
    exit 1
fi
echo "[完成] 数据文件已保存到: ./migrate.zip"

echo
echo "[成功] v1数据导出完成!"
echo "[文件] 导出文件: ./migrate.zip"
echo "[提示] 下一步: 请将migrate.zip和迁移工具复制到v2容器中进行导入"
echo