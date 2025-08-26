#!/bin/bash
# filepath: import_v2_data.sh

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'      # 红色 - 错误
GREEN='\033[0;32m'    # 绿色 - 成功
YELLOW='\033[1;33m'   # 黄色 - 提示
BLUE='\033[0;34m'     # 蓝色 - 示例
CYAN='\033[0;36m'     # 青色 - 用法
MAGENTA='\033[0;35m'  # 紫色 - 步骤
NC='\033[0m'          # 无颜色 - 重置

echo "=== MaxKB v2 数据导入脚本 ==="
echo

# 检查是否提供了容器名称参数
if [ -z "$1" ]; then
    echo -e "${RED}[错误]${NC} 未提供容器名称"
    echo -e "${CYAN}[用法]${NC} $0 <v2_container_name>"
    echo -e "${BLUE}[示例]${NC} $0 maxkb"
    echo -e "${YELLOW}[提示]${NC} 使用 'docker ps' 查看当前运行的容器"
    exit 1
fi

V2_CONTAINER="$1"
echo "[信息] 使用指定的容器: $V2_CONTAINER"
echo "[确认] 目标容器: $V2_CONTAINER"
echo

# 检查容器是否存在且运行中
if ! docker ps --format "{{.Names}}" | grep -q "^$V2_CONTAINER$"; then
    echo -e "${RED}[错误]${NC} 容器 $V2_CONTAINER 未运行或不存在"
    echo -e "${YELLOW}[提示]${NC} 使用 'docker ps' 查看当前运行的容器"
    exit 1
fi

# 检查迁移数据文件是否存在
if [ ! -f "./migrate.zip" ]; then
    echo -e "${RED}[错误]${NC} 迁移数据文件 ./migrate.zip 不存在"
    echo -e "${YELLOW}[提示]${NC} 请先运行 export_v1_data.sh 导出v1数据"
    exit 1
fi

# 复制迁移数据文件到v2容器
echo -e "${MAGENTA}[步骤1]${NC} 复制迁移数据文件到v2容器..."
if ! docker cp . "$V2_CONTAINER":/opt/maxkb-app/v1-to-v2-migrator; then
    echo -e "${RED}[错误]${NC} 复制迁移数据文件失败"
    exit 1
fi
echo -e "${GREEN}[完成]${NC} 迁移数据文件复制完成"

# 在v2容器中导入数据
echo -e "${MAGENTA}[步骤2]${NC} 在v2容器中导入数据..."
if ! docker exec -w /opt/maxkb-app/v1-to-v2-migrator "$V2_CONTAINER" python migrate.py import; then
    echo -e "${RED}[错误]${NC} 数据导入失败"
    exit 1
fi
echo -e "${GREEN}[完成]${NC} 数据导入完成"

# 清理v2容器中的临时文件
echo -e "${MAGENTA}[步骤3]${NC} 清理临时文件..."
docker exec "$V2_CONTAINER" rm -rf /opt/maxkb-app/v1-to-v2-migrator/migrate.zip 2>/dev/null || true
echo -e "${GREEN}[完成]${NC} 临时文件清理完成"

echo
echo -e "${GREEN}[成功]${NC} v1数据导入到v2完成!"
echo -e "${YELLOW}[提示]${NC} 请重启v2容器以确保所有更改生效"
echo
echo "建议的重启命令:"
echo -e "${BLUE}  docker restart $V2_CONTAINER${NC}"
echo