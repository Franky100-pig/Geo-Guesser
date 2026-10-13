#!/usr/bin/env bash
#
# geo.sh — Geo-Guesser 一键启动器 / one-command launcher
#
# 你只需要做两件事：
#   1. 把照片放进本项目文件夹
#   2. 在终端运行这一条命令：
#        bash geo.sh 照片.jpg
#
# 不用懂 uv、不用设环境变量、不用管"国内/国外"两条通道——脚本会自动选。
# 如果一眼看出是"国内街景"且想更快出结果，可加 cn：
#        bash geo.sh 照片.jpg cn
#
# Usage / 用法:
#   bash geo.sh 照片.jpg            # 自动（国内/国外都支持，最稳妥）
#   bash geo.sh 照片.jpg cn         # 已知是国内照片 → 更快的国内通道
#   bash geo.sh 照片.jpg world      # 强制国外高精度通道
#
set -euo pipefail

PHOTO="${1:-}"
MODE="${2:-auto}"   # auto | cn | world

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- 0) 参数检查 ----------------------------------------------------------
if [[ -z "$PHOTO" || ! -f "$PHOTO" ]]; then
  echo "用法 / Usage:  bash geo.sh 照片.jpg [cn|world]"
  echo "示例 / Example: bash geo.sh vacation.jpg"
  echo "示例 / Example: bash geo.sh beijing.jpg cn"
  exit 1
fi

# --- 1) 定位 geo-sleuth 技能 ---------------------------------------------
SKILL="${GEO_SLEUTH_SKILL:-$HOME/.workbuddy/skills/geo-sleuth}"
if [[ ! -d "$SKILL" ]]; then
  echo "✗ 没找到 geo-sleuth 技能，请先安装："
  echo "    https://github.com/Oldcircle/geo-sleuth"
  echo "  （默认应装在：${SKILL}）"
  exit 1
fi

# --- 2) 检查 uv（一次性工具）---------------------------------------------
if ! command -v uv >/dev/null 2>&1; then
  echo "✗ 需要先装 uv（一次性，约 10 秒）："
  echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "  装完重开终端，再运行本命令即可。"
  exit 1
fi

# --- 3) 选通道并运行 ------------------------------------------------------
echo "=========================================="
echo " Geo-Guesser · 照片位置分析"
echo " 照片 / Photo : $PHOTO"
echo "=========================================="
case "$MODE" in
  cn)
    echo "▶ 国内快速通道 (CN fast lane)"
    bash "$SELF_DIR/gg_fast.sh" "$PHOTO"
    ;;
  world)
    echo "▶ 国外高精度通道 (worldwide accuracy lane)"
    bash "$SELF_DIR/global_accuracy.sh" "$PHOTO"
    ;;
  auto|*)
    echo "▶ 自动通道（国内/国外都支持，最稳妥）"
    echo "  若一眼看出是国内街景、想更快，可加 cn："
    echo "    bash geo.sh $(basename "$PHOTO") cn"
    bash "$SELF_DIR/global_accuracy.sh" "$PHOTO"
    ;;
esac
