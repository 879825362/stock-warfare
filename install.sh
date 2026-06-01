#!/bin/bash
# 股票战法 - 一键安装脚本
# 数据源：同花顺 THS（thsdk），替代东方财富/akshare

set -e

echo "=================================="
echo "  股票战法技能包 安装脚本"
echo "=================================="
echo ""

# 1. 安装 Python 依赖
echo ">>> 检查 Python 依赖..."
pip3 install thsdk MyTT pandas numpy 2>/dev/null
echo "    Python 依赖安装完成"

# 2. 安装战法命令
echo ">>> 安装战法命令..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.claude/commands"

# 如果用户在项目级别用 Claude Code，也装一份到当前目录
if [ -n "$CLAUDE_PROJECT_DIR" ]; then
    mkdir -p "$CLAUDE_PROJECT_DIR/.claude/commands"
    cp "$SCRIPT_DIR/commands/"*.md "$CLAUDE_PROJECT_DIR/.claude/commands/"
    echo "    已安装到项目: $CLAUDE_PROJECT_DIR/.claude/commands/"
fi

cp "$SCRIPT_DIR/commands/"*.md "$HOME/.claude/commands/"
echo "    已安装到全局: ~/.claude/commands/"

echo ""
echo "=================================="
echo "  安装完成！"
echo "  重启 Claude Code 生效"
echo "=================================="
echo ""
echo "数据源：同花顺 THS（游客模式免配置）"
echo ""
echo "使用方法："
echo "  /个股查询"
echo "  /今日热门板块"