#!/bin/bash
# filepath: export_v1_data.sh

set -e  # 遇到错误立即退出

# 定义颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo "=== MaxKB v1 数据导出脚本 ==="
echo

# 检查是否提供了容器名称参数
if [ -z "$1" ]; then
    echo -e "${RED}[错误]${NC} 未提供容器名称"
    echo -e "${BLUE}[用法]${NC} $0 <v1_container_name>"
    echo -e "${CYAN}[示例]${NC} $0 maxkb"
    echo -e "${YELLOW}[提示]${NC} 使用 'docker ps' 查看当前运行的容器"
    exit 1
fi

V1_CONTAINER="$1"
echo "[信息] 使用指定的容器: $V1_CONTAINER"
echo "[确认] 目标容器: $V1_CONTAINER"
echo

# 检查容器是否存在且运行中
if ! docker ps --format "{{.Names}}" | grep -q "^$V1_CONTAINER$"; then
    echo -e "${RED}[错误]${NC} 容器 $V1_CONTAINER 未运行或不存在"
    echo -e "${YELLOW}[提示]${NC} 使用 'docker ps' 查看当前运行的容器"
    exit 1
fi

# 复制迁移工具到v1容器
echo -e "${MAGENTA}[步骤1]${NC} 复制迁移工具到v1容器..."
if ! docker cp . "$V1_CONTAINER":/opt/maxkb/app/v1-to-v2-migrator; then
    echo -e "${RED}[错误]${NC} 复制迁移工具失败"
    exit 1
fi
echo -e "${GREEN}[完成]${NC} 迁移工具复制完成"

# 在v1容器中导出数据
echo -e "${MAGENTA}[步骤2]${NC} 在v1容器中导出数据..."
if ! docker exec -w /opt/maxkb/app/v1-to-v2-migrator "$V1_CONTAINER" python migrate.py export; then
    echo -e "${RED}[错误]${NC} 数据导出失败"
    exit 1
fi
echo -e "${GREEN}[完成]${NC} 数据导出完成"

# 复制数据到主机
echo -e "${MAGENTA}[步骤3]${NC} 复制导出的数据到主机..."
if ! docker cp "$V1_CONTAINER":/opt/maxkb/app/v1-to-v2-migrator/migrate.zip ./migrate.zip; then
    echo -e "${RED}[错误]${NC} 复制数据文件失败"
    exit 1
fi
echo -e "${GREEN}[完成]${NC} 数据文件已保存到: ./migrate.zip"

echo
echo -e "${GREEN}[成功]${NC} v1数据导出完成!"
echo "[文件] 导出文件: ./migrate.zip"
echo -e "${YELLOW}[提示]${NC} 下一步: 请将migrate.zip和迁移工具复制到v2容器中进行导入