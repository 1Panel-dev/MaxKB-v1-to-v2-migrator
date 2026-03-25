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

# 计时工具函数
_step_start=0
step_start() {
    _step_start=$(date +%s)
}
step_end() {
    local elapsed=$(( $(date +%s) - _step_start ))
    echo -e "${CYAN}[耗时]${NC} ${elapsed} 秒"
}

SCRIPT_START=$(date +%s)

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
step_start
if ! docker cp . "$V1_CONTAINER":/opt/maxkb/app/v1-to-v2-migrator; then
    echo -e "${RED}[错误]${NC} 复制迁移工具失败"
    exit 1
fi
step_end
echo -e "${GREEN}[完成]${NC} 迁移工具复制完成"

# 在v1容器中导出数据
echo -e "${MAGENTA}[步骤2]${NC} 在v1容器中导出数据..."
step_start
if ! docker exec -w /opt/maxkb/app/v1-to-v2-migrator "$V1_CONTAINER" python migrate.py export; then
    echo -e "${RED}[错误]${NC} 数据导出失败"
    exit 1
fi
step_end
echo -e "${GREEN}[完成]${NC} 数据导出完成"

# 复制数据到主机
echo -e "${MAGENTA}[步骤3]${NC} 复制导出的数据到主机..."
step_start
v1_data=$(docker inspect "$V1_CONTAINER" --format '{{.GraphDriver.Data.UpperDir}}')
migrate_tar="${v1_data}/opt/maxkb/app/v1-to-v2-migrator/migrate.tar"

if [ -f "$migrate_tar" ]; then
    echo "[信息] 通过容器文件系统路径复制: $migrate_tar"
    if ! cp "$migrate_tar" ./migrate.tar; then
        echo -e "${RED}[错误]${NC} 复制数据文件失败"
        exit 1
    fi
else
    echo "[信息] 通过 docker cp 复制..."
    if ! docker cp "$V1_CONTAINER":/opt/maxkb/app/v1-to-v2-migrator/migrate.tar ./migrate.tar; then
        echo -e "${RED}[错误]${NC} 复制数据文件失败"
        exit 1
    fi
fi
step_end
echo -e "${GREEN}[完成]${NC} 数据文件已保存到: ./migrate.tar"

echo
TOTAL_ELAPSED=$(( $(date +%s) - SCRIPT_START ))
echo -e "${GREEN}[成功]${NC} v1数据导出完成! 总耗时: ${TOTAL_ELAPSED} 秒"
echo "[文件] 导出文件: ./migrate.tar"
echo -e "${YELLOW}[提示]${NC} 下一步: 请将migrate.tar和迁移工具复制到v2容器中进行导入"
echo